"""
Payment views
"""
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
        
        # Update payment status
        from payments.models import Payment
        payment = Payment.objects(moyasar_payment_id=payment_id).first()
        if payment:
            if payment_status == 'paid':
                payment.status = 'completed'
                payment.order_id.payment_status = 'completed'
                payment.order_id.save()
            elif payment_status == 'failed':
                payment.status = 'failed'
                payment.order_id.payment_status = 'failed'
                payment.order_id.save()
            payment.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

