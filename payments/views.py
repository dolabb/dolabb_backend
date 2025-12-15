"""
Payment views
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from payments.services import MoyasarPaymentService
from products.services import OrderService
from products.models import Order, Product


@api_view(['POST'])
def checkout(request):
    """Create checkout/order"""
    try:
        buyer_id = str(request.user.id)
        order = OrderService.create_order(buyer_id, request.data)

        # Build a user-friendly summary for products in the order
        # For single-item orders, keep existing behavior (product title)
        # For multi-item cart orders, show a combined label
        product_label = order.product_title or ""
        try:
            # item_count defaults to 1 in the model for backward compatibility
            if hasattr(order, "item_count") and order.item_count and order.item_count > 1:
                # Example: "3 items in your cart"
                product_label = f"{order.item_count} items in your cart"
        except Exception:
            # If anything goes wrong, fall back to original title
            product_label = order.product_title or ""
        return Response({
            'success': True,
            'orderId': str(order.id),
            'checkoutData': {
                'product': product_label,
                'size': '',  # TODO: Add size if available
                'price': order.price,
                'offerPrice': order.offer_price,
                'shipping': order.shipping_cost,
                'platformFee': order.dolabb_fee,
                'affiliateCode': order.affiliate_code or '',
                'total': order.total_price,
                'currency': order.currency or 'SAR'  # Include currency in checkout response
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def process_payment(request):
    """Process payment via Moyasar"""
    try:
        order_id = request.data.get('orderId')
        token_id = request.data.get('tokenId')
        card_details = request.data.get('cardDetails')
        amount = request.data.get('amount')
        description = request.data.get('description')
        metadata = request.data.get('metadata', {})
        
        if not order_id:
            return Response({'success': False, 'error': 'Order ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not token_id and not card_details:
            return Response({'success': False, 'error': 'Either tokenId or cardDetails is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment, payment_data = MoyasarPaymentService.process_payment(
            order_id, card_details, token_id, amount, description, metadata
        )
        
        return Response({
            'success': True,
            'payment': {
                'id': str(payment.id),
                'status': payment.status,
                'amount': payment.amount,
                'currency': payment.currency,
                'source': payment_data.get('source', {}),
                'order': {
                    'id': str(payment.order_id.id),
                    'orderNumber': payment.order_id.order_number
                }
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def payment_webhook(request):
    """Handle Moyasar webhook - Verifies payment status with Moyasar API before processing"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Moyasar-Signature', '')
        payload = request.body
        
        # Verify and process webhook
        # MoyasarPaymentService.verify_webhook(signature, payload)
        
        data = request.data
        logger.info(f"Webhook received data: {data}")
        
        # Handle nested data structure (data.data) or flat structure
        payment_data = data.get('data', data)
        
        payment_id = payment_data.get('id') or data.get('id')
        # Don't trust status from frontend - we'll verify with Moyasar
        frontend_status = payment_data.get('status') or data.get('status')
        amount = payment_data.get('amount', data.get('amount', 0))
        
        # Extract offerId from request data if provided (frontend can send it)
        offer_id_from_request = data.get('offerId') or data.get('offer_id') or payment_data.get('offerId')
        
        logger.info(f"Extracted payment_id: {payment_id}, frontend_status: {frontend_status}, offerId: {offer_id_from_request}")
        
        if not payment_id:
            logger.error("Payment ID not found in webhook data")
            return Response({
                'success': False,
                'error': 'Payment ID not found in webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # CRITICAL: Verify payment status with Moyasar API - don't trust frontend status
        logger.info(f"Verifying payment status with Moyasar API for payment_id: {payment_id}")
        try:
            verified_payment_data = MoyasarPaymentService.verify_payment_status(payment_id)
            payment_status = verified_payment_data.get('status')
            logger.info(f"✅ Verified payment status from Moyasar: {payment_status} (frontend sent: {frontend_status})")
            
            # Use verified payment data instead of frontend data
            payment_data = verified_payment_data
            amount = payment_data.get('amount', amount)
        except Exception as e:
            logger.error(f"❌ Failed to verify payment status with Moyasar: {str(e)}")
            # If verification fails, we can't trust the payment status
            return Response({
                'success': False,
                'error': f'Failed to verify payment status with Moyasar: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not payment_status:
            logger.error("Payment status not found in Moyasar response")
            return Response({
                'success': False,
                'error': 'Payment status not found in Moyasar response'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle failed payments - don't process further, just return success to stop retries
        if payment_status in ['failed', 'declined', 'canceled', 'cancelled']:
            logger.warning(f"Payment {payment_id} has status '{payment_status}' - marking as failed")
            
            # Extract error information from Moyasar response
            error_message = None
            error_code = None
            
            # Check source errors first (most common location for card errors in Moyasar)
            if 'source' in payment_data:
                source = payment_data.get('source', {})
                if 'message' in source:
                    error_message = source.get('message')
                    logger.info(f"Found error message in source.message: {error_message}")
                if 'response_code' in source:
                    error_code = source.get('response_code')
                    logger.info(f"Found error code in source.response_code: {error_code}")
                if 'transaction' in source:
                    source_transaction = source.get('transaction', {})
                    if 'message' in source_transaction:
                        error_message = source_transaction.get('message') or error_message
                    if 'code' in source_transaction:
                        error_code = source_transaction.get('code') or error_code
            
            # Check transaction errors
            if not error_message and 'transaction' in payment_data:
                transaction = payment_data.get('transaction', {})
                error_message = transaction.get('message') or error_message
                error_code = transaction.get('code') or error_code
            
            # Check top-level error fields
            if not error_message:
                error_message = (
                    payment_data.get('message') or 
                    payment_data.get('error') or 
                    payment_data.get('description') or
                    payment_data.get('error_message')
                )
            
            # If still no error code, try response_code at top level
            if not error_code:
                error_code = payment_data.get('response_code') or payment_data.get('code')
            
            logger.info(f"Extracted error details - message: {error_message}, code: {error_code}")
            
            buyer_id_to_notify = None
            
            try:
                # Try to update payment status to failed if payment exists
                from payments.models import Payment
                payment = Payment.objects(moyasar_payment_id=payment_id).first()
                if payment:
                    payment.status = 'failed'
                    # Store full Moyasar response in metadata for error details
                    payment.metadata = payment_data
                    payment.save()
                    logger.info(f"Payment {payment_id} marked as failed")
                    
                    # Get buyer_id from payment
                    if payment.order_id:
                        buyer_id_to_notify = str(payment.order_id.buyer_id.id)
                        payment.order_id.payment_status = 'failed'
                        payment.order_id.save()
                        logger.info(f"Order {payment.order_id.id} payment status marked as failed")
                
                # If payment not found, try to find order by payment_id or metadata
                if not buyer_id_to_notify:
                    from products.models import Order
                    # Try to find order by payment_id
                    order = Order.objects(payment_id=payment_id).first()
                    
                    # If not found, try to find by offerId from metadata
                    if not order:
                        metadata = payment_data.get('metadata', {})
                        offer_id = offer_id_from_request or metadata.get('offerId') or metadata.get('offer_id')
                        if offer_id:
                            from products.models import Offer
                            offer = Offer.objects(id=offer_id).first()
                            if offer:
                                order = Order.objects(offer_id=offer.id).first()
                    
                    # If still not found, try order_id from metadata
                    if not order:
                        metadata = payment_data.get('metadata', {})
                        order_id = metadata.get('order_id') or metadata.get('orderId')
                        if order_id:
                            order = Order.objects(id=order_id).first()
                    
                    if order:
                        buyer_id_to_notify = str(order.buyer_id.id)
                        order.payment_status = 'failed'
                        order.save()
                        logger.info(f"Order {order.id} payment status marked as failed")
                
                # Send payment failed email with Moyasar error details
                if buyer_id_to_notify:
                    try:
                        from notifications.notification_helper import NotificationHelper
                        logger.info(f"❌ Payment failed - sending email with Moyasar error details to buyer {buyer_id_to_notify}")
                        
                        # Send payment failed email with error details
                        NotificationHelper.send_payment_failed_with_details(
                            buyer_id=buyer_id_to_notify,
                            error_message=error_message,
                            error_code=error_code,
                            moyasar_response=payment_data
                        )
                        logger.info(f"✅ Payment failed email sent with error details")
                    except Exception as e:
                        logger.error(f"Error sending payment failed email: {str(e)}")
                else:
                    logger.warning(f"Could not find buyer_id to send payment failed email for payment {payment_id}")
            except Exception as e:
                logger.error(f"Error updating failed payment: {str(e)}")
            
            # Return success to prevent Moyasar from retrying failed payments
            return Response({
                'success': True,
                'message': f'Payment {payment_status} - no further processing needed',
                'data': {
                    'payment_id': payment_id,
                    'status': payment_status,
                    'updated': False
                }
            }, status=status.HTTP_200_OK)
        
        # Update payment status using the service method (only for successful payments)
        updated = MoyasarPaymentService.update_payment_status(payment_id, payment_status)
        logger.info(f"Payment status update result: {updated}")
        
        # Extract offerId from multiple sources (request, metadata, payment_data)
        metadata = payment_data.get('metadata', {}) or data.get('metadata', {})
        offer_id_final = (
            offer_id_from_request or 
            metadata.get('offerId') or 
            metadata.get('offer_id') or
            payment_data.get('offerId') or
            data.get('offerId')
        )
        
        # If we have offerId and payment is paid, update offer status directly (even if order not found)
        if payment_status == 'paid' and offer_id_final:
            from products.models import Offer as OfferModel
            offer = OfferModel.objects(id=offer_id_final).first()
            if offer:
                if offer.status != 'paid':
                    logger.info(f"Directly updating offer {offer.id} status from '{offer.status}' to 'paid' (from offerId: {offer_id_final})")
                    offer.status = 'paid'
                    offer.updated_at = datetime.utcnow()
                    offer.save()
                    logger.info(f"✅ Directly updated offer {offer.id} status to 'paid'")
                else:
                    logger.info(f"Offer {offer.id} already has status 'paid'")
            else:
                logger.warning(f"Offer not found with ID: {offer_id_final}")
        
        # If update was successful, verify offer status was updated
        if updated and payment_status == 'paid':
            from payments.models import Payment as PaymentModel
            from products.models import Order as OrderModel, Offer as OfferModel
            payment_check = PaymentModel.objects(moyasar_payment_id=payment_id).first()
            if payment_check and payment_check.order_id and payment_check.order_id.offer_id:
                offer_check = OfferModel.objects(id=payment_check.order_id.offer_id.id).first()
                if offer_check and offer_check.status != 'paid':
                    logger.warning(f"Offer {offer_check.id} status is still '{offer_check.status}', forcing update to 'paid'")
                    offer_check.status = 'paid'
                    offer_check.updated_at = datetime.utcnow()
                    offer_check.save()
                    logger.info(f"✅ Force updated offer {offer_check.id} status to 'paid'")
        
        if not updated:
            logger.warning(f"Payment not found with moyasar_payment_id: {payment_id}, fetching full payment details from Moyasar")
            # Fetch full payment details from Moyasar API to get metadata
            try:
                full_payment_data = MoyasarPaymentService.verify_payment_status(payment_id)
                logger.info(f"Fetched full payment data from Moyasar: {full_payment_data.get('id')}")
                # Use full payment data which includes metadata
                payment_data = full_payment_data
                amount = payment_data.get('amount', amount)
            except Exception as e:
                logger.warning(f"Could not fetch payment from Moyasar: {str(e)}, using webhook data")
            
            # If payment not found, try to find order by payment_id in order.payment_id
            from payments.models import Payment
            from products.models import Order, Offer
            
            # Try to find order by payment_id
            order = Order.objects(payment_id=payment_id).first()
            if order:
                logger.info(f"Found order {order.id} by payment_id")
            
            # If not found, try to find by offerId from metadata
            if not order:
                metadata = payment_data.get('metadata', {})
                offer_id = offer_id_from_request or metadata.get('offerId') or metadata.get('offer_id')
                logger.info(f"Looking for order by offerId from metadata/request: {offer_id}")
                
                if offer_id:
                    # Find offer
                    offer = Offer.objects(id=offer_id).first()
                    if offer:
                        logger.info(f"Found offer {offer.id}, looking for associated order")
                        # Find order by offer_id
                        order = Order.objects(offer_id=offer.id).first()
                        if order:
                            logger.info(f"Found order {order.id} by offer_id")
                        else:
                            logger.warning(f"No order found for offer {offer.id}")
                    else:
                        logger.warning(f"Offer not found: {offer_id}")
            
            # If still not found, try to find by metadata order_id
            if not order:
                order_id = payment_data.get('metadata', {}).get('order_id') or data.get('metadata', {}).get('order_id')
                if order_id:
                    logger.info(f"Trying to find order by order_id: {order_id}")
                    order = Order.objects(id=order_id).first()
            
            if order:
                logger.info(f"Found order {order.id}")
                # Create payment record if it doesn't exist
                existing_payment = Payment.objects(moyasar_payment_id=payment_id).first()
                if not existing_payment:
                    # Get currency from order first, then payment_data, then default to SAR
                    payment_currency = order.currency or payment_data.get('currency') or 'SAR'
                    payment = Payment(
                        order_id=order.id,
                        buyer_id=order.buyer_id.id,
                        moyasar_payment_id=payment_id,
                        amount=float(amount) / 100 if amount else 0,
                        currency=payment_currency,
                        status='completed' if payment_status == 'paid' else 'pending',
                        metadata=payment_data
                    )
                    payment.save()
                    logger.info(f"Created payment record for order {order.id}")
                else:
                    logger.info(f"Payment record already exists: {existing_payment.id}")
                
                # Update order payment_id if not set
                if not order.payment_id:
                    order.payment_id = payment_id
                    order.save()
                    logger.info(f"Updated order {order.id} payment_id")
                
                # Update status - this will update payment, order, and offer
                updated = MoyasarPaymentService.update_payment_status(payment_id, payment_status)
                logger.info(f"Payment status update after creation: {updated}")
            else:
                logger.error(f"Could not find order for payment {payment_id}. Payment data: {payment_data}")
                # Still return success to avoid webhook retries, but log the error
                return Response({
                    'success': True,
                    'message': 'Webhook received but order not found',
                    'data': {
                        'payment_id': payment_id,
                        'status': payment_status,
                        'updated': False,
                        'warning': 'Order not found - payment record may need manual update'
                    }
                }, status=status.HTTP_200_OK)
        
        # Final verification: Ensure offer status is updated if payment is paid
        # Only send emails if Moyasar confirms payment status is 'paid'
        if payment_status == 'paid':
            from products.models import Offer as OfferModel
            
            # Try to find offer from order (if order exists)
            if updated:
                from payments.models import Payment as PaymentModel
                from products.models import Order as OrderModel
                payment_check = PaymentModel.objects(moyasar_payment_id=payment_id).first()
                if payment_check and payment_check.order_id:
                    order_check = payment_check.order_id
                    
                    # Send email notifications only when Moyasar confirms payment is 'paid'
                    try:
                        from notifications.notification_helper import NotificationHelper
                        logger.info(f"✅ Payment confirmed as 'paid' by Moyasar - sending email notifications")
                        # Notify seller - payment confirmed
                        NotificationHelper.send_payment_confirmed(str(order_check.seller_id.id))
                        # Notify seller - order needs shipping
                        NotificationHelper.send_order_needs_shipping(str(order_check.seller_id.id))
                        # Notify buyer - payment successful
                        NotificationHelper.send_payment_successful(str(order_check.buyer_id.id), order_check)
                        logger.info(f"✅ Email notifications sent successfully")
                    except Exception as e:
                        logger.error(f"Error sending payment notifications: {str(e)}")
                    
                    if order_check.offer_id:
                        offer_check = OfferModel.objects(id=order_check.offer_id.id).first()
                        if offer_check and offer_check.status != 'paid':
                            logger.warning(f"Final check: Offer {offer_check.id} status is still '{offer_check.status}', forcing update")
                            offer_check.status = 'paid'
                            offer_check.updated_at = datetime.utcnow()
                            offer_check.save()
                            logger.info(f"✅ Final update: Offer {offer_check.id} status set to 'paid'")
                        elif offer_check:
                            logger.info(f"Final verification - Offer {offer_check.id} status: '{offer_check.status}'")
            
            # Also try to update offer directly from offerId if we have it
            if offer_id_final:
                offer_final = OfferModel.objects(id=offer_id_final).first()
                if offer_final and offer_final.status != 'paid':
                    logger.info(f"Final check: Updating offer {offer_final.id} status to 'paid' from offerId")
                    offer_final.status = 'paid'
                    offer_final.updated_at = datetime.utcnow()
                    offer_final.save()
                    logger.info(f"✅ Final update: Offer {offer_final.id} status set to 'paid'")
        
        return Response({
            'success': True,
            'message': 'Webhook processed successfully',
            'data': {
                'payment_id': payment_id,
                'status': payment_status,
                'updated': updated,
                'offerId': offer_id_final
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Payment webhook error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_payment(request):
    """Verify payment status from Moyasar and update local records"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        moyasar_payment_id = request.data.get('paymentId') or request.data.get('payment_id')
        
        if not moyasar_payment_id:
            return Response({
                'success': False,
                'error': 'Payment ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Verifying payment: {moyasar_payment_id}")
        
        # Verify payment status from Moyasar
        payment_data = MoyasarPaymentService.verify_payment_status(moyasar_payment_id)
        
        # Log full payment data for debugging
        logger.info(f"Full Moyasar payment response: {payment_data}")
        
        # Extract status - check multiple possible locations
        payment_status = (
            payment_data.get('status') or 
            payment_data.get('payment', {}).get('status') or
            payment_data.get('body', {}).get('status') or
            payment_data.get('data', {}).get('status')
        )
        
        logger.info(f"Extracted payment status from Moyasar: '{payment_status}'")
        
        # If status is still None, log warning and try to infer from other fields
        if not payment_status:
            logger.warning(f"Payment status not found in expected locations. Full response keys: {list(payment_data.keys())}")
            # Check if there's an error or failure indicator
            if payment_data.get('source', {}).get('message') and 'DECLINED' in str(payment_data.get('source', {}).get('message', '')).upper():
                payment_status = 'failed'
                logger.info(f"Inferred status as 'failed' from source message")
        
        if not payment_status:
            logger.error(f"Could not determine payment status from Moyasar response")
            return Response({
                'success': False,
                'error': 'Could not determine payment status from Moyasar response'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle failed payments first - send failed email and keep order pending
        if payment_status.lower() in ['failed', 'declined', 'canceled', 'cancelled']:
            logger.warning(f"Payment {moyasar_payment_id} has status '{payment_status}' - handling as failed")
            
            # Extract error information from Moyasar response
            error_message = None
            error_code = None
            
            # Check source errors first (most common location for card errors in Moyasar)
            if 'source' in payment_data:
                source = payment_data.get('source', {})
                if 'message' in source:
                    error_message = source.get('message')
                    logger.info(f"Found error message in source.message: {error_message}")
                if 'response_code' in source:
                    error_code = source.get('response_code')
                    logger.info(f"Found error code in source.response_code: {error_code}")
                if 'transaction' in source:
                    source_transaction = source.get('transaction', {})
                    if 'message' in source_transaction:
                        error_message = source_transaction.get('message') or error_message
                    if 'code' in source_transaction:
                        error_code = source_transaction.get('code') or error_code
            
            # Check transaction errors
            if not error_message and 'transaction' in payment_data:
                transaction = payment_data.get('transaction', {})
                error_message = transaction.get('message') or error_message
                error_code = transaction.get('code') or error_code
            
            # Check top-level error fields
            if not error_message:
                error_message = (
                    payment_data.get('message') or 
                    payment_data.get('error') or 
                    payment_data.get('description') or
                    payment_data.get('error_message')
                )
            
            # If still no error code, try response_code at top level
            if not error_code:
                error_code = payment_data.get('response_code') or payment_data.get('code')
            
            logger.info(f"Final extracted error details - message: '{error_message}', code: '{error_code}'")
            
            buyer_id_to_notify = None
            
            # Try to find order and buyer
            from payments.models import Payment
            from products.models import Order, Offer
            
            payment = Payment.objects(moyasar_payment_id=moyasar_payment_id).first()
            if payment and payment.order_id:
                buyer_id_to_notify = str(payment.order_id.buyer_id.id)
                # Mark payment as failed but keep order as pending
                payment.status = 'failed'
                payment.metadata = payment_data
                payment.save()
                # Keep order payment_status as pending (don't mark as failed)
                if payment.order_id.payment_status != 'pending':
                    payment.order_id.payment_status = 'pending'
                    payment.order_id.save()
                logger.info(f"Payment {moyasar_payment_id} marked as failed, order kept as pending")
            else:
                # Try to find order by payment_id or metadata
                order = Order.objects(payment_id=moyasar_payment_id).first()
                
                if not order:
                    offer_id_from_request = request.data.get('offerId') or request.data.get('offer_id')
                    metadata = payment_data.get('metadata', {})
                    offer_id = offer_id_from_request or metadata.get('offerId') or metadata.get('offer_id')
                    if offer_id:
                        offer = Offer.objects(id=offer_id).first()
                        if offer:
                            order = Order.objects(offer_id=offer.id).first()
                
                if not order:
                    order_id = request.data.get('orderId') or request.data.get('order_id')
                    if order_id:
                        order = Order.objects(id=order_id).first()
                
                if order:
                    buyer_id_to_notify = str(order.buyer_id.id)
                    # Create payment record with failed status
                    if not payment:
                        # Get currency from order first, then payment_data, then default to SAR
                        payment_currency = order.currency or payment_data.get('currency') or 'SAR'
                        payment = Payment(
                            order_id=order.id,
                            buyer_id=order.buyer_id.id,
                            moyasar_payment_id=moyasar_payment_id,
                            amount=float(payment_data.get('amount', 0)) / 100,
                            currency=payment_currency,
                            status='failed',
                            metadata=payment_data
                        )
                        payment.save()
                    # Keep order payment_status as pending
                    if order.payment_status != 'pending':
                        order.payment_status = 'pending'
                        order.save()
                    logger.info(f"Order {order.id} kept as pending, payment marked as failed")
            
            # Send payment failed email with error details (ONLY email for failed payments)
            if buyer_id_to_notify:
                try:
                    from notifications.notification_helper import NotificationHelper
                    logger.info(f"❌ Payment failed - sending failed payment email to buyer {buyer_id_to_notify}")
                    logger.info(f"Error message: '{error_message}', Error code: '{error_code}'")
                    result = NotificationHelper.send_payment_failed_with_details(
                        buyer_id=buyer_id_to_notify,
                        error_message=error_message,
                        error_code=error_code,
                        moyasar_response=payment_data
                    )
                    if result:
                        logger.info(f"✅ Payment failed email sent successfully to buyer {buyer_id_to_notify}")
                    else:
                        logger.warning(f"⚠️ Payment failed email function returned None for buyer {buyer_id_to_notify}")
                except Exception as e:
                    logger.error(f"❌ Error sending payment failed email: {str(e)}", exc_info=True)
            else:
                logger.error(f"❌ Cannot send failed payment email - buyer_id_to_notify is None for payment {moyasar_payment_id}")
                logger.error(f"Payment data: {payment_data}")
                logger.error(f"Payment record exists: {payment is not None}")
                if payment:
                    logger.error(f"Payment has order_id: {payment.order_id is not None if payment else False}")
            
            return Response({
                'success': True,
                'payment': {
                    'id': moyasar_payment_id,
                    'status': payment_status,
                    'updated': False,
                    'error_message': error_message,
                    'error_code': error_code
                },
                'message': 'Payment verification completed - payment failed',
                'email_sent': buyer_id_to_notify is not None
            }, status=status.HTTP_200_OK)
        
        # Handle successful payments (status is 'paid' or 'authorized')
        updated = False
        if payment_status.lower() in ['paid', 'authorized']:
            logger.info(f"✅ Payment {moyasar_payment_id} has status '{payment_status}' - processing as successful")
            
            # Update payment status for successful payments
            updated = MoyasarPaymentService.update_payment_status(moyasar_payment_id, payment_status)
            logger.info(f"Payment status update result: {updated}")
        else:
            logger.warning(f"⚠️ Payment {moyasar_payment_id} has unexpected status '{payment_status}' - treating as pending")
            # For other statuses (like 'initiated', 'pending'), keep as pending
            updated = False
        
        if not updated:
            logger.warning(f"Payment not found, trying to find/create payment record")
            from payments.models import Payment
            from products.models import Order, Offer
            
            # Try to find order by payment_id first
            order = Order.objects(payment_id=moyasar_payment_id).first()
            
            # If not found, try to find by offerId from metadata or request
            if not order:
                offer_id_from_request = request.data.get('offerId') or request.data.get('offer_id')
                metadata = payment_data.get('metadata', {})
                offer_id = offer_id_from_request or metadata.get('offerId') or metadata.get('offer_id')
                logger.info(f"Looking for order by offerId from metadata/request: {offer_id}")
                
                if offer_id:
                    # Find offer
                    offer = Offer.objects(id=offer_id).first()
                    if offer:
                        logger.info(f"Found offer {offer.id}, looking for associated order")
                        # Find order by offer_id
                        order = Order.objects(offer_id=offer.id).first()
                        if order:
                            logger.info(f"Found order {order.id} by offer_id")
                        else:
                            logger.warning(f"No order found for offer {offer.id}")
                    else:
                        logger.warning(f"Offer not found: {offer_id}")
            
            # If still not found, try order_id from request
            if not order:
                order_id = request.data.get('orderId') or request.data.get('order_id')
                if order_id:
                    logger.info(f"Trying to find order by order_id: {order_id}")
                    order = Order.objects(id=order_id).first()
            
            if order:
                logger.info(f"Found order {order.id}, creating/updating payment record")
                # Check if payment exists
                payment = Payment.objects(moyasar_payment_id=moyasar_payment_id).first()
                if not payment:
                    # Create payment record
                    # Get currency from order first, then payment_data, then default to SAR
                    payment_currency = order.currency or payment_data.get('currency') or 'SAR'
                    payment = Payment(
                        order_id=order.id,
                        buyer_id=order.buyer_id.id,
                        moyasar_payment_id=moyasar_payment_id,
                        amount=float(payment_data.get('amount', 0)) / 100,
                        currency=payment_currency,
                        status='completed' if payment_status == 'paid' else 'pending',
                        metadata=payment_data
                    )
                    payment.save()
                    logger.info(f"Created payment record for order {order.id}")
                else:
                    logger.info(f"Payment record already exists: {payment.id}")
                
                # Update order payment_id if not set
                if not order.payment_id:
                    order.payment_id = moyasar_payment_id
                    order.save()
                    logger.info(f"Updated order {order.id} payment_id")
                
                # Update status - this will update payment, order, and offer
                updated = MoyasarPaymentService.update_payment_status(moyasar_payment_id, payment_status)
                logger.info(f"Payment status update after creation: {updated}")
                
                # Send order confirmation emails ONLY when payment is confirmed as 'paid'
                if payment_status == 'paid' and updated:
                    try:
                        from notifications.notification_helper import NotificationHelper
                        logger.info(f"✅ Payment confirmed as 'paid' by Moyasar - sending order confirmation emails")
                        # Notify seller - item sold (only when payment is confirmed)
                        NotificationHelper.send_item_sold(str(order.seller_id.id))
                        # Notify buyer - order confirmation (only when payment is confirmed)
                        NotificationHelper.send_order_confirmation(str(order.buyer_id.id), order)
                        # Notify seller - payment confirmed
                        NotificationHelper.send_payment_confirmed(str(order.seller_id.id))
                        # Notify seller - order needs shipping
                        NotificationHelper.send_order_needs_shipping(str(order.seller_id.id))
                        # Notify buyer - payment successful
                        NotificationHelper.send_payment_successful(str(order.buyer_id.id), order)
                        logger.info(f"✅ All order confirmation emails sent successfully")
                    except Exception as e:
                        logger.error(f"Error sending order confirmation emails: {str(e)}")
            else:
                logger.error(f"Could not find order for payment {moyasar_payment_id}")
        
        return Response({
            'success': True,
            'payment': {
                'id': moyasar_payment_id,
                'status': payment_status,
                'updated': updated
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        logger.error(f"Verify payment ValueError: {str(e)}")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Verify payment error: {str(e)}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def payment_success(request):
    """
    Get payment success/failure details with product information
    Accepts order_id or payment_id (moyasar_payment_id) as parameter
    """
    from payments.models import Payment
    
    try:
        # Get order_id or payment_id from query params (GET) or body (POST)
        order_id = request.GET.get('orderId') or request.data.get('orderId') or request.GET.get('order_id') or request.data.get('order_id')
        payment_id = request.GET.get('paymentId') or request.data.get('paymentId') or request.GET.get('payment_id') or request.data.get('payment_id')
        moyasar_payment_id = request.GET.get('moyasarPaymentId') or request.data.get('moyasarPaymentId') or request.GET.get('moyasar_payment_id') or request.data.get('moyasar_payment_id')
        
        payment = None
        order = None
        
        # Find payment by moyasar_payment_id first
        if moyasar_payment_id:
            payment = Payment.objects(moyasar_payment_id=moyasar_payment_id).first()
            if payment:
                order = payment.order_id
        
        # If not found, try payment_id (local payment ID)
        if not payment and payment_id:
            payment = Payment.objects(id=payment_id).first()
            if payment:
                order = payment.order_id
        
        # If not found, try order_id
        if not order and order_id:
            order = Order.objects(id=order_id).first()
            if order:
                # Find payment for this order
                if order.payment_id:
                    payment = Payment.objects(moyasar_payment_id=order.payment_id).first()
                if not payment:
                    payment = Payment.objects(order_id=order.id).first()
        
        if not order:
            return Response({
                'success': False,
                'error': 'Order not found. Please provide orderId, paymentId, or moyasarPaymentId'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get product details
        product = Product.objects(id=order.product_id.id).first()
        if not product:
            return Response({
                'success': False,
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get product image (first image from images array)
        product_image = product.images[0] if product.images and len(product.images) > 0 else ''
        
        # Extract error information from Moyasar metadata if payment failed
        error_message = None
        error_code = None
        error_details = None
        
        if payment and payment.metadata:
            moyasar_data = payment.metadata
            # Moyasar error information is typically in these fields
            if payment.status == 'failed':
                error_message = moyasar_data.get('message') or moyasar_data.get('error') or moyasar_data.get('description')
                error_code = moyasar_data.get('code') or moyasar_data.get('error_code')
                
                # Check for transaction errors
                if 'transaction' in moyasar_data:
                    transaction = moyasar_data.get('transaction', {})
                    error_message = transaction.get('message') or error_message
                    error_code = transaction.get('code') or error_code
                
                # Check for source errors (card errors)
                if 'source' in moyasar_data:
                    source = moyasar_data.get('source', {})
                    if 'message' in source:
                        error_message = source.get('message') or error_message
                    if 'transaction' in source:
                        source_transaction = source.get('transaction', {})
                        error_message = source_transaction.get('message') or error_message
                        error_code = source_transaction.get('code') or error_code
                
                # Get full error details
                error_details = {
                    'message': error_message,
                    'code': error_code,
                    'status': moyasar_data.get('status'),
                    'type': moyasar_data.get('type')
                }
        
        # Determine paid amount
        paid_amount = None
        if payment:
            if payment.status == 'completed':
                paid_amount = float(payment.amount)
            elif payment.status == 'failed':
                paid_amount = 0.0
        else:
            # If no payment record, check order payment status
            if order.payment_status == 'completed':
                paid_amount = float(order.total_price)
            else:
                paid_amount = 0.0
        
        # Build response
        response_data = {
            'success': True,
            'order': {
                'id': str(order.id),
                'orderNumber': order.order_number,
                'status': order.status,
                'paymentStatus': order.payment_status
            },
            'product': {
                'id': str(product.id),
                'title': product.title,
                'image': product_image,
                'price': float(product.price),
                'originalPrice': float(product.original_price) if product.original_price else None
            },
            'payment': {
                'status': payment.status if payment else order.payment_status,
                'paidAmount': paid_amount,
                'currency': payment.currency if payment else 'SAR',
                'moyasarPaymentId': payment.moyasar_payment_id if payment else order.payment_id
            }
        }
        
        # Add error information if payment failed
        if (payment and payment.status == 'failed') or (order.payment_status == 'failed'):
            response_data['error'] = {
                'hasError': True,
                'message': error_message or 'Payment processing failed',
                'code': error_code,
                'details': error_details
            }
        else:
            response_data['error'] = {
                'hasError': False
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment success API error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

