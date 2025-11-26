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
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Moyasar-Signature', '')
        payload = request.body
        
        # Verify and process webhook
        # MoyasarPaymentService.verify_webhook(signature, payload)
        
        data = request.data
        payment_id = data.get('id')
        payment_status = data.get('status')
        
        # Update payment status using the service method
        updated = MoyasarPaymentService.update_payment_status(payment_id, payment_status)
        
        if not updated:
            # If payment not found, try to create it from order_id if provided
            order_id = data.get('metadata', {}).get('order_id')
            if order_id:
                from payments.models import Payment
                from products.models import Order
                order = Order.objects(id=order_id).first()
                if order:
                    # Create payment record if it doesn't exist
                    payment = Payment(
                        order_id=order_id,
                        buyer_id=order.buyer_id.id,
                        moyasar_payment_id=payment_id,
                        amount=float(data.get('amount', 0)) / 100,
                        currency=data.get('currency', 'SAR'),
                        status='completed' if payment_status == 'paid' else 'pending',
                        metadata=data
                    )
                    payment.save()
                    # Update status
                    MoyasarPaymentService.update_payment_status(payment_id, payment_status)
        
        return Response({'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        import logging
        logging.error(f"Payment webhook error: {str(e)}")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_payment(request):
    """Verify payment status from Moyasar and update local records"""
    try:
        moyasar_payment_id = request.data.get('paymentId') or request.data.get('payment_id')
        
        if not moyasar_payment_id:
            return Response({
                'success': False,
                'error': 'Payment ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment status from Moyasar
        payment_data = MoyasarPaymentService.verify_payment_status(moyasar_payment_id)
        payment_status = payment_data.get('status')
        
        # Update payment status
        updated = MoyasarPaymentService.update_payment_status(moyasar_payment_id, payment_status)
        
        if not updated:
            # Try to find or create payment record by order_id
            order_id = request.data.get('orderId') or request.data.get('order_id')
            if order_id:
                from payments.models import Payment
                from products.models import Order
                order = Order.objects(id=order_id).first()
                if order:
                    # Check if payment exists
                    payment = Payment.objects(order_id=order_id).first()
                    if not payment:
                        # Create payment record
                        payment = Payment(
                            order_id=order_id,
                            buyer_id=order.buyer_id.id,
                            moyasar_payment_id=moyasar_payment_id,
                            amount=float(payment_data.get('amount', 0)) / 100,
                            currency=payment_data.get('currency', 'SAR'),
                            status='completed' if payment_status == 'paid' else 'pending',
                            metadata=payment_data
                        )
                        payment.save()
                    
                    # Update status
                    MoyasarPaymentService.update_payment_status(moyasar_payment_id, payment_status)
                    updated = True
        
        return Response({
            'success': True,
            'payment': {
                'id': moyasar_payment_id,
                'status': payment_status,
                'updated': updated
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import logging
        logging.error(f"Verify payment error: {str(e)}")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

