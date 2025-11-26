"""
Payment views
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from payments.services import MoyasarPaymentService
from products.services import OrderService
from products.models import Order


@api_view(['POST'])
def checkout(request):
    """Create checkout/order"""
    try:
        buyer_id = str(request.user.id)
        order = OrderService.create_order(buyer_id, request.data)
        
        return Response({
            'success': True,
            'orderId': str(order.id),
            'checkoutData': {
                'product': order.product_title,
                'size': '',  # TODO: Add size if available
                'price': order.price,
                'offerPrice': order.offer_price,
                'shipping': order.shipping_cost,
                'platformFee': order.dolabb_fee,
                'affiliateCode': order.affiliate_code or '',
                'total': order.total_price
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
    """Handle Moyasar webhook"""
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
        payment_status = payment_data.get('status') or data.get('status')
        amount = payment_data.get('amount', data.get('amount', 0))
        
        # Extract offerId from request data if provided (frontend can send it)
        offer_id_from_request = data.get('offerId') or data.get('offer_id') or payment_data.get('offerId')
        
        logger.info(f"Extracted payment_id: {payment_id}, status: {payment_status}, offerId: {offer_id_from_request}")
        
        if not payment_id:
            logger.error("Payment ID not found in webhook data")
            return Response({
                'success': False,
                'error': 'Payment ID not found in webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not payment_status:
            logger.error("Payment status not found in webhook data")
            return Response({
                'success': False,
                'error': 'Payment status not found in webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update payment status using the service method
        updated = MoyasarPaymentService.update_payment_status(payment_id, payment_status)
        logger.info(f"Payment status update result: {updated}")
        
        # If we have offerId and payment is paid, update offer status directly (even if order not found)
        if payment_status == 'paid' and offer_id_from_request:
            from products.models import Offer as OfferModel
            offer = OfferModel.objects(id=offer_id_from_request).first()
            if offer:
                if offer.status != 'paid':
                    logger.info(f"Directly updating offer {offer.id} status from '{offer.status}' to 'paid' (from offerId in request)")
                    offer.status = 'paid'
                    offer.updated_at = datetime.utcnow()
                    offer.save()
                    logger.info(f"✅ Directly updated offer {offer.id} status to 'paid'")
                else:
                    logger.info(f"Offer {offer.id} already has status 'paid'")
            else:
                logger.warning(f"Offer not found with ID: {offer_id_from_request}")
        
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
                    payment = Payment(
                        order_id=order.id,
                        buyer_id=order.buyer_id.id,
                        moyasar_payment_id=payment_id,
                        amount=float(amount) / 100 if amount else 0,
                        currency=payment_data.get('currency', 'SAR'),
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
        
        # Verify the update was successful by checking if offer status was updated
        if updated and payment_status == 'paid':
            from payments.models import Payment
            from products.models import Order, Offer
            # Double-check that offer status was updated
            payment_check = Payment.objects(moyasar_payment_id=payment_id).first()
            if payment_check and payment_check.order_id and payment_check.order_id.offer_id:
                offer_check = Offer.objects(id=payment_check.order_id.offer_id.id).first()
                if offer_check:
                    logger.info(f"Final verification - Offer {offer_check.id} status: '{offer_check.status}'")
        
        return Response({
            'success': True,
            'message': 'Webhook processed successfully',
            'data': {
                'payment_id': payment_id,
                'status': payment_status,
                'updated': updated
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
        payment_status = payment_data.get('status')
        logger.info(f"Payment status from Moyasar: {payment_status}")
        
        # Update payment status
        updated = MoyasarPaymentService.update_payment_status(moyasar_payment_id, payment_status)
        logger.info(f"Payment status update result: {updated}")
        
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
                    payment = Payment(
                        order_id=order.id,
                        buyer_id=order.buyer_id.id,
                        moyasar_payment_id=moyasar_payment_id,
                        amount=float(payment_data.get('amount', 0)) / 100,
                        currency=payment_data.get('currency', 'SAR'),
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
                
                # Update status
                updated = MoyasarPaymentService.update_payment_status(moyasar_payment_id, payment_status)
                logger.info(f"Payment status update after creation: {updated}")
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

