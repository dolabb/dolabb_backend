"""
Payment services
"""
import requests
from datetime import datetime
from django.conf import settings
from payments.models import Payment
from products.models import Order, Offer
from products.services import OrderService


class MoyasarPaymentService:
    """Moyasar payment service"""
    
    # Moyasar supported currencies
    MOYASAR_SUPPORTED_CURRENCIES = ['SAR', 'USD', 'EUR', 'GBP', 'KWD', 'AED', 'OMR', 'QAR']
    
    @staticmethod
    def process_payment(
        order_id,
        card_details=None,
        token_id=None,
        amount=None,
        description=None,
        metadata=None,
    ):
        """
        Process payment via Moyasar for a single order.
        """
        order = Order.objects(id=order_id).first()
        if not order:
            raise ValueError("Order not found")

        order_currency = order.currency or 'SAR'

        if not amount:
            amount = order.total_price * 100  # Convert to cents/fils
        
        # Check if required settings are available
        if not hasattr(settings, 'MOYASAR_API_URL') or not settings.MOYASAR_API_URL:
            raise ValueError(
                "MOYASAR_API_URL setting is missing. "
                "Please add MOYASAR_API_URL to your Django settings (default: 'https://api.moyasar.com/v1/payments')"
            )
        if not hasattr(settings, 'MOYASAR_SECRET_KEY') or not settings.MOYASAR_SECRET_KEY:
            raise ValueError(
                "MOYASAR_SECRET_KEY setting is missing. "
                "Please add MOYASAR_SECRET_KEY to your environment variables."
            )
        
        url = settings.MOYASAR_API_URL
        
        headers = {
            'Authorization': f'Bearer {settings.MOYASAR_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'amount': int(amount),
            'currency': order_currency,
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
                order_id=order.id,
                buyer_id=order.buyer_id.id,
                amount=amount / 100,
                currency=order_currency,
                moyasar_payment_id=payment_data.get('id'),
                status='completed' if payment_data.get('status') == 'paid' else 'pending',
                metadata=payment_data,
            )
            payment.save()

            # Update payment status on order
            order.payment_status = payment.status
            order.payment_id = payment_data.get('id')
            # Set order status to 'packed' after payment is completed
            if payment.status == 'completed':
                order.status = 'packed'
            order.save()
            
            # Send notifications based on payment status
            try:
                from notifications.notification_helper import NotificationHelper
                if payment.status == 'completed':
                    # Notify seller - payment confirmed
                    NotificationHelper.send_payment_confirmed(str(order.seller_id.id))
                    # Notify seller - order needs shipping
                    NotificationHelper.send_order_needs_shipping(str(order.seller_id.id))
                    # Notify buyer - payment successful
                    NotificationHelper.send_payment_successful(str(order.buyer_id.id), order)
                elif payment.status == 'failed':
                    # Notify buyer - payment failed
                    NotificationHelper.send_payment_failed(str(order.buyer_id.id))
            except Exception as e:
                import logging
                logging.error(f"Error sending payment notifications: {str(e)}")
            
            # Update offer status from 'accepted' to 'paid' if order has an associated offer
            if payment.status == 'completed' and order.offer_id:
                offer = Offer.objects(id=order.offer_id.id).first()
                if offer and offer.status == 'accepted':
                    offer.status = 'paid'
                    offer.updated_at = datetime.utcnow()
                    offer.save()
            
            # Note: Affiliate earnings are NOT updated on payment completion
            # They will be updated when buyer submits review AND seller has uploaded shipment_proof
            # This ensures earnings are only credited when the transaction is fully completed
            
            return payment, payment_data
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Payment processing failed: {str(e)}")
    
    @staticmethod
    def verify_payment_status(moyasar_payment_id):
        """Verify payment status from Moyasar API"""
        try:
            # Check if required settings are available
            if not hasattr(settings, 'MOYASAR_API_URL') or not settings.MOYASAR_API_URL:
                raise ValueError(
                    "MOYASAR_API_URL setting is missing. "
                    "Please add MOYASAR_API_URL to your Django settings (default: 'https://api.moyasar.com/v1/payments')"
                )
            if not hasattr(settings, 'MOYASAR_SECRET_KEY') or not settings.MOYASAR_SECRET_KEY:
                raise ValueError(
                    "MOYASAR_SECRET_KEY setting is missing. "
                    "Please add MOYASAR_SECRET_KEY to your environment variables in Render dashboard. "
                    "Format: sk_live_xxxxxxxxxxxxx (for production) or sk_test_xxxxxxxxxxxxx (for testing)"
                )
            
            # Validate secret key format and strip whitespace
            secret_key = settings.MOYASAR_SECRET_KEY.strip() if settings.MOYASAR_SECRET_KEY else None
            
            if not secret_key:
                raise ValueError(
                    "MOYASAR_SECRET_KEY is empty or None. "
                    "Please check your Render environment variables."
                )
            
            # Log first few characters for debugging (without exposing full key)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Using MOYASAR_SECRET_KEY starting with: {secret_key[:15]}... (length: {len(secret_key)})")
            
            if not secret_key.startswith(('sk_live_', 'sk_test_')):
                raise ValueError(
                    f"Invalid MOYASAR_SECRET_KEY format. "
                    f"Expected format: sk_live_xxxxxxxxxxxxx or sk_test_xxxxxxxxxxxxx. "
                    f"Current value starts with: {secret_key[:20] if len(secret_key) > 20 else secret_key}"
                )
            
            url = f"{settings.MOYASAR_API_URL}/{moyasar_payment_id}"
            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Calling Moyasar API: {url}")
            
            response = requests.get(url, headers=headers)
            
            # Handle 401 Unauthorized specifically
            if response.status_code == 401:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Moyasar API returned 401 Unauthorized. Secret key starts with: {secret_key[:15]}...")
                logger.error(f"Response body: {response.text[:200] if hasattr(response, 'text') else 'N/A'}")
                raise ValueError(
                    f"Moyasar API authentication failed (401 Unauthorized). "
                    f"Secret key starts with: {secret_key[:15]}... "
                    f"Please verify: 1) Key is set correctly in Render (no quotes/spaces), "
                    f"2) Key matches your Moyasar dashboard, 3) Key is for the correct environment (live/test), "
                    f"4) Payment ID belongs to the same Moyasar account"
                )
            
            response.raise_for_status()
            payment_data = response.json()
            
            return payment_data
        except AttributeError as e:
            raise ValueError(f"Configuration error: {str(e)}. Please check your Django settings.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    f"Moyasar API authentication failed (401 Unauthorized). "
                    f"Please verify MOYASAR_SECRET_KEY in Render environment variables. "
                    f"Error: {str(e)}"
                )
            raise ValueError(f"Failed to verify payment status: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to verify payment status: {str(e)}")
    
    @staticmethod
    def update_payment_status(moyasar_payment_id, payment_status):
        """Update payment, order, and offer status when payment is completed"""
        import logging
        logger = logging.getLogger(__name__)
        
        from products.services import OrderService
        from products.models import Order
        
        # Find payment by moyasar_payment_id
        payment = Payment.objects(moyasar_payment_id=moyasar_payment_id).first()
        
        # If payment not found, try to find order by payment_id
        if not payment:
            logger.warning(f"Payment not found with moyasar_payment_id: {moyasar_payment_id}")
            # Try to find order by payment_id
            order = Order.objects(payment_id=moyasar_payment_id).first()
            if order:
                logger.info(f"Found order {order.id} by payment_id, creating payment record")
                # Get currency from order, default to SAR if not set
                order_currency = order.currency or 'SAR'
                # Create payment record
                payment = Payment(
                    order_id=order.id,
                    buyer_id=order.buyer_id.id,
                    moyasar_payment_id=moyasar_payment_id,
                    amount=order.total_price,
                    currency=order_currency,
                    status='completed' if payment_status == 'paid' else 'pending',
                    metadata={}
                )
                payment.save()
                logger.info(f"Created payment record for order {order.id}")
            else:
                logger.error(f"Could not find payment or order with moyasar_payment_id: {moyasar_payment_id}")
                return False
        
        logger.info(f"Updating payment status: {moyasar_payment_id} -> {payment_status}")
        logger.info(f"Payment record: {payment.id}, Order: {payment.order_id.id}")

        if payment_status == 'paid':
            payment.status = 'completed'
            order = payment.order_id
            order.payment_status = 'completed'
            # Set order status to 'packed' after payment is completed
            order.status = 'packed'
            order.save()
            logger.info(f"Order {order.id} status updated to 'packed', payment_status: 'completed'")
            
            # Update offer status from 'accepted' to 'paid' if order has an associated offer
            if order.offer_id:
                offer_id = order.offer_id.id
                logger.info(f"Order has associated offer: {offer_id}")
                offer = Offer.objects(id=offer_id).first()
                if offer:
                    logger.info(f"Found offer {offer.id}, current status: '{offer.status}'")
                    if offer.status != 'paid':
                        # Update offer status to 'paid' when payment is completed
                        logger.info(f"Updating offer {offer.id} status from '{offer.status}' to 'paid'")
                        offer.status = 'paid'
                        offer.updated_at = datetime.utcnow()
                        offer.save()
                        logger.info(f"✅ Offer {offer.id} status successfully updated to 'paid'")
                    else:
                        logger.info(f"Offer {offer.id} already has status 'paid'")
                else:
                    logger.warning(f"❌ Offer not found for ID: {offer_id}")
            else:
                logger.info(f"Order {order.id} has no associated offer_id")
            
            # Update affiliate earnings when payment is completed
            OrderService.update_affiliate_earnings_on_payment_completion(order)
        elif payment_status in ['failed', 'declined', 'canceled', 'cancelled']:
            payment.status = 'failed'
            # Keep order payment_status as 'pending' - don't mark as failed
            # Order should remain pending until payment is successful
            order = payment.order_id
            if order.payment_status != 'pending':
                order.payment_status = 'pending'
                order.save()
            logger.info(f"Payment {moyasar_payment_id} marked as failed, order kept as pending")
        
        payment.save()
        logger.info(f"Payment {payment.id} saved successfully")
        return True
    
    @staticmethod
    def verify_webhook(signature, payload):
        """Verify webhook signature (if Moyasar provides webhook verification)"""
        # Implement webhook verification if needed
        return True
    
    @staticmethod
    def create_payout(amount, currency, destination, purpose='payout', metadata=None):
        """
        Create a payout via Moyasar API
        
        Args:
            amount: Payout amount in the smallest currency unit (e.g., for 1.00 SAR, use 100)
            currency: Currency code (SAR, USD, etc.)
            destination: Dictionary containing destination details:
                - type: 'bank' or 'wallet'
                - iban: IBAN for bank transfers (required for type='bank')
                - name: Beneficiary name (required)
                - mobile: Mobile number (optional)
                - country: Country code (optional)
                - city: City name (optional)
            purpose: Purpose of the payout (default: 'payout')
            metadata: Additional metadata (optional)
        
        Returns:
            Dictionary containing Moyasar payout response
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if required settings are available
        if not hasattr(settings, 'MOYASAR_SECRET_KEY') or not settings.MOYASAR_SECRET_KEY:
            raise ValueError(
                "MOYASAR_SECRET_KEY setting is missing. "
                "Please add MOYASAR_SECRET_KEY to your environment variables."
            )
        
        # Get payout API URL (default to standard Moyasar API)
        payout_api_url = getattr(settings, 'MOYASAR_PAYOUT_API_URL', 'https://api.moyasar.com/v1/payouts')
        
        # Get payout source ID (required for payouts)
        payout_source_id = getattr(settings, 'MOYASAR_PAYOUT_SOURCE_ID', None)
        if not payout_source_id:
            raise ValueError(
                "MOYASAR_PAYOUT_SOURCE_ID setting is missing. "
                "Please add MOYASAR_PAYOUT_SOURCE_ID to your environment variables. "
                "This is the ID of your payout account in Moyasar."
            )
        
        url = payout_api_url
        
        headers = {
            'Authorization': f'Bearer {settings.MOYASAR_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Build payload
        payload = {
            'source_id': payout_source_id,
            'amount': int(amount),
            'currency': currency,
            'purpose': purpose,
            'destination': destination,
        }
        
        if metadata:
            payload['metadata'] = metadata
        
        try:
            logger.info(f"Creating Moyasar payout: {amount} {currency} to {destination.get('name', 'N/A')}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            payout_data = response.json()
            logger.info(f"Moyasar payout created successfully: {payout_data.get('id')}")
            return payout_data
        except requests.exceptions.HTTPError as e:
            error_msg = f"Payout creation failed: {str(e)}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                    logger.error(f"Moyasar payout error: {error_data}")
                except:
                    error_msg = f"Payout creation failed: {e.response.text}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Payout creation failed: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def parse_account_details(account_details_str):
        """
        Parse account details string to extract bank account information.
        Supports both JSON format and plain text format.
        
        Args:
            account_details_str: String containing account details (JSON or plain text)
        
        Returns:
            Dictionary with parsed account details:
                - iban: IBAN number
                - name: Account holder name
                - mobile: Mobile number (optional)
                - country: Country code (optional, defaults to 'SA' for Saudi Arabia)
                - city: City name (optional)
        """
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        if not account_details_str:
            raise ValueError("Account details are required for payout")
        
        # Try to parse as JSON first
        try:
            account_data = json.loads(account_details_str)
            if isinstance(account_data, dict):
                # Extract IBAN (check multiple possible keys)
                iban = (
                    account_data.get('iban') or 
                    account_data.get('IBAN') or 
                    account_data.get('account_number') or 
                    account_data.get('accountNumber') or
                    account_data.get('bank_account') or
                    account_data.get('bankAccount')
                )
                
                # Extract name
                name = (
                    account_data.get('name') or 
                    account_data.get('account_holder') or 
                    account_data.get('accountHolder') or
                    account_data.get('holder_name') or
                    account_data.get('holderName')
                )
                
                # Extract optional fields
                mobile = account_data.get('mobile') or account_data.get('phone')
                country = account_data.get('country') or account_data.get('country_code') or 'SA'
                city = account_data.get('city')
                
                return {
                    'iban': iban,
                    'name': name,
                    'mobile': mobile,
                    'country': country,
                    'city': city
                }
        except json.JSONDecodeError:
            # Not JSON, treat as plain text
            logger.info("Account details not in JSON format, parsing as plain text")
            pass
        
        # If not JSON or parsing failed, treat as plain text
        # Assume the string might contain IBAN or account number
        # For plain text, we'll try to extract IBAN pattern (SA followed by 22 digits)
        import re
        iban_match = re.search(r'SA\d{22}', account_details_str.replace(' ', '').upper())
        iban = iban_match.group(0) if iban_match else account_details_str.strip()
        
        # For plain text, we'll use the full string as IBAN and try to extract name
        # This is a fallback - ideally account_details should be in JSON format
        lines = account_details_str.strip().split('\n')
        name = lines[0] if lines else 'Account Holder'
        
        return {
            'iban': iban,
            'name': name,
            'mobile': None,
            'country': 'SA',
            'city': None
        }

