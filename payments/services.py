"""
Payment services
"""
import requests
from django.conf import settings
from payments.models import Payment
from products.models import Order
from products.services import OrderService


class MoyasarPaymentService:
    """Moyasar payment service"""
    
    @staticmethod
    def process_payment(order_id, card_details=None, token_id=None, amount=None, description=None, metadata=None):
        """Process payment via Moyasar"""
        order = Order.objects(id=order_id).first()
        if not order:
            raise ValueError("Order not found")
        
        if not amount:
            amount = order.total_price * 100  # Convert to cents/fils
        
        url = settings.MOYASAR_API_URL
        
        headers = {
            'Authorization': f'Bearer {settings.MOYASAR_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'amount': int(amount),
            'currency': 'SAR',
            'description': description or f'Order {order.order_number}',
            'metadata': metadata or {}
        }
        
        if token_id:
            payload['source'] = {
                'type': 'token',
                'token': token_id
            }
        elif card_details:
            payload['source'] = {
                'type': 'creditcard',
                'name': card_details.get('name'),
                'number': card_details.get('number'),
                'month': card_details.get('month'),
                'year': card_details.get('year'),
                'cvc': card_details.get('cvc')
            }
        else:
            raise ValueError("Either token_id or card_details must be provided")
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            payment_data = response.json()
            
            # Create payment record
            payment = Payment(
                order_id=order_id,
                buyer_id=order.buyer_id.id,
                amount=amount / 100,
                currency='SAR',
                moyasar_payment_id=payment_data.get('id'),
                status='completed' if payment_data.get('status') == 'paid' else 'pending',
                metadata=payment_data
            )
            payment.save()
            
            # Update order payment status
            order.payment_status = payment.status
            order.payment_id = payment_data.get('id')
            order.save()
            
            # Update affiliate earnings if payment is completed
            if payment.status == 'completed':
                from products.services import OrderService
                OrderService.update_affiliate_earnings_on_payment_completion(order)
            
            return payment, payment_data
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Payment processing failed: {str(e)}")
    
    @staticmethod
    def verify_webhook(signature, payload):
        """Verify webhook signature (if Moyasar provides webhook verification)"""
        # Implement webhook verification if needed
        return True

