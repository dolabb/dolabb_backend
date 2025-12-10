"""
Notification Helper Service
Automatically sends notifications to users when actions are performed
"""
from datetime import datetime
from notifications.models import UserNotification
from notifications.templates import get_notification_template
from notifications.email_templates import send_notification_email
from authentication.models import User, Affiliate
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class NotificationHelper:
    """Helper class for sending automatic notifications"""
    
    @staticmethod
    def send_notification_to_user(user_id, category, template_key, user_type='user', extra_message=None):
        """
        Send notification to a specific user
        
        Args:
            user_id: User ID (string or ObjectId)
            category: 'seller', 'buyer', or 'affiliate'
            template_key: Key from templates (e.g., 'item_sold', 'order_confirmation')
            user_type: 'user' or 'affiliate' - determines which model to use
        
        Returns:
            UserNotification object or None if failed
        """
        try:
            # Get user based on type first to get language preference
            if user_type == 'affiliate':
                user = Affiliate.objects(id=user_id).first()
                if not user:
                    print(f"Warning: Affiliate not found with id={user_id}")
                    return None
                # Affiliates don't have language field, default to 'en'
                user_language = 'en'
            else:
                user = User.objects(id=user_id).first()
                if not user:
                    print(f"Warning: User not found with id={user_id}")
                    return None
                # Get user's language preference, default to 'en'
                user_language = getattr(user, 'language', 'en')
                if user_language not in ['en', 'ar']:
                    user_language = 'en'
            
            # Get template with user's language
            template = get_notification_template(category, template_key, user_language)
            if not template:
                print(f"Warning: Template not found for category={category}, key={template_key}")
                return None

            # Append extra details if provided
            message = template['message']
            if extra_message:
                message = f"{message}<br><br>{extra_message}"
            
            # Create user notification
            user_notification = UserNotification(
                user_id=user.id,
                title=template['title'],
                message=message,
                notification_type=template['type'],
                delivered_at=datetime.utcnow()
            )
            user_notification.save()
            
            # Send via WebSocket
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{user.id}',
                        {
                            'type': 'send_notification',
                            'notification': {
                                'id': str(user_notification.id),
                                'title': user_notification.title,
                                'message': user_notification.message,
                                'type': user_notification.notification_type,
                                'createdAt': user_notification.created_at.isoformat()
                            }
                        }
                    )
            except Exception as e:
                print(f"Warning: Failed to send WebSocket notification: {str(e)}")
            
            # Send email notification via Resend (mandatory)
            try:
                if hasattr(user, 'email') and user.email:
                    # Get user name for personalized greeting
                    user_name = None
                    if hasattr(user, 'name') and user.name:
                        user_name = user.name
                    elif hasattr(user, 'username') and user.username:
                        user_name = user.username
                    elif hasattr(user, 'first_name') and user.first_name:
                        user_name = user.first_name
                    
                    # Determine notification type for email styling
                    email_notification_type = 'info'
                    if 'success' in template['title'].lower() or 'approved' in template['title'].lower() or 'confirmed' in template['title'].lower():
                        email_notification_type = 'success'
                    elif 'failed' in template['title'].lower() or 'error' in template['title'].lower() or 'rejected' in template['title'].lower():
                        email_notification_type = 'error'
                    elif 'warning' in template['title'].lower() or 'violation' in template['title'].lower():
                        email_notification_type = 'warning'
                    
                    send_notification_email(
                        email=user.email,
                        notification_title=template['title'],
                            notification_message=message,
                        notification_type=email_notification_type,
                        user_name=user_name,
                        language=user_language
                    )
            except Exception as e:
                print(f"Warning: Failed to send email notification: {str(e)}")
            
            return user_notification
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return None
    
    @staticmethod
    def send_seller_verification_approved(seller_id):
        """Send seller verification approved notification"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'seller_verification_approved'
        )
    
    @staticmethod
    def send_bank_payment_setup_completed(user_id, user_type='user'):
        """Send bank/payment setup completed notification"""
        category = 'affiliate' if user_type == 'affiliate' else 'seller'
        return NotificationHelper.send_notification_to_user(
            user_id, category, 'bank_payment_setup_completed', user_type
        )
    
    @staticmethod
    def send_listing_published(seller_id):
        """Send listing published notification"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'listing_published'
        )
    
    @staticmethod
    def send_item_sold(seller_id):
        """Send item sold notification to seller"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'item_sold'
        )
    
    @staticmethod
    def send_payment_confirmed(seller_id):
        """Send payment confirmed notification to seller"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'payment_confirmed'
        )
    
    @staticmethod
    def send_order_needs_shipping(seller_id):
        """Send order needs shipping notification"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'order_needs_shipping'
        )
    
    @staticmethod
    def send_buyer_rejected_order(seller_id):
        """Send buyer rejected order notification"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'buyer_rejected_order'
        )
    
    @staticmethod
    def send_buyer_confirmed_delivery(seller_id):
        """Send buyer confirmed delivery notification"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'buyer_confirmed_delivery'
        )
    
    @staticmethod
    def send_new_offer_received(seller_id):
        """Send new offer received notification to seller"""
        return NotificationHelper.send_notification_to_user(
            seller_id, 'seller', 'new_offer_received'
        )
    
    @staticmethod
    def send_counter_offer_received(user_id, user_role='seller'):
        """Send counter offer received notification"""
        category = 'seller' if user_role == 'seller' else 'buyer'
        return NotificationHelper.send_notification_to_user(
            user_id, category, 'counter_offer_received'
        )
    
    @staticmethod
    def send_dispute_resolved(user_id, user_role='seller'):
        """Send dispute resolved notification"""
        category = 'seller' if user_role == 'seller' else 'buyer'
        return NotificationHelper.send_notification_to_user(
            user_id, category, 'dispute_resolved'
        )
    
    @staticmethod
    def send_payout_sent(user_id, user_type='user'):
        """Send payout sent notification"""
        category = 'affiliate' if user_type == 'affiliate' else 'seller'
        key = 'affiliate_payout_sent' if user_type == 'affiliate' else 'payout_sent'
        return NotificationHelper.send_notification_to_user(
            user_id, category, key, user_type
        )
    
    @staticmethod
    def send_payout_failed(user_id, user_type='user'):
        """Send payout failed notification"""
        category = 'affiliate' if user_type == 'affiliate' else 'seller'
        key = 'affiliate_payout_failed' if user_type == 'affiliate' else 'payout_failed'
        return NotificationHelper.send_notification_to_user(
            user_id, category, key, user_type
        )
    
    @staticmethod
    def send_policy_violation_warning(user_id, user_type='user'):
        """Send policy violation warning"""
        category = 'affiliate' if user_type == 'affiliate' else 'seller'
        key = 'affiliate_policy_violation' if user_type == 'affiliate' else 'policy_violation_warning'
        return NotificationHelper.send_notification_to_user(
            user_id, category, key, user_type
        )
    
    # BUYER Notifications
    @staticmethod
    def send_welcome_email(user_id):
        """Send welcome email notification"""
        return NotificationHelper.send_notification_to_user(
            user_id, 'buyer', 'welcome_email'
        )
    
    @staticmethod
    def _build_order_detail_message(order):
        """
        Build a detailed message snippet with product, totals, and shipping info.
        Safe to call with None; returns empty string if order is missing.
        """
        if not order:
            return ''

        try:
            # Lazy import to avoid circular dependency
            from products.models import Product

            # Try to fetch product to enrich the message
            product_title = getattr(order, 'product_title', '') or ''
            product_obj = None
            if getattr(order, 'product_id', None):
                product_obj = Product.objects(id=order.product_id.id).first()
                if product_obj and product_obj.title:
                    product_title = product_obj.title

            # Basic pricing details
            total_price = getattr(order, 'total_price', None)
            shipping_cost = getattr(order, 'shipping_cost', None)
            offer_price = getattr(order, 'offer_price', None)
            order_number = getattr(order, 'order_number', '')

            # Delivery address is stored as a string; include if present
            delivery_address = getattr(order, 'delivery_address', '') or ''

            parts = []
            if order_number:
                parts.append(f"Order Number: {order_number}")
            if product_title:
                parts.append(f"Product: {product_title}")
            if offer_price is not None:
                parts.append(f"Item Price: {offer_price} SAR")
            if shipping_cost is not None:
                parts.append(f"Shipping: {shipping_cost} SAR")
            if total_price is not None:
                parts.append(f"Total: {total_price} SAR")
            if delivery_address:
                parts.append(f"Delivery Address: {delivery_address}")

            if not parts:
                return ''

            return "<br>".join(parts)
        except Exception:
            # If anything fails, fall back silently to avoid blocking notifications
            return ''

    @staticmethod
    def send_order_confirmation(buyer_id, order=None):
        """Send order confirmation notification with optional order details"""
        detail_message = NotificationHelper._build_order_detail_message(order)

        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'order_confirmation', extra_message=detail_message
        )
    
    @staticmethod
    def send_payment_successful(buyer_id, order=None):
        """Send payment successful notification with optional order details"""
        detail_message = NotificationHelper._build_order_detail_message(order)

        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'payment_successful', extra_message=detail_message
        )
    
    @staticmethod
    def send_seller_shipped_item(buyer_id):
        """Send seller shipped item notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'seller_shipped_item'
        )
    
    @staticmethod
    def send_item_delivered(buyer_id):
        """Send item delivered notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'item_delivered'
        )
    
    @staticmethod
    def send_order_canceled(buyer_id):
        """Send order canceled notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'order_canceled'
        )
    
    @staticmethod
    def send_offer_accepted(buyer_id):
        """Send offer accepted notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'offer_accepted'
        )
    
    @staticmethod
    def send_offer_declined(buyer_id):
        """Send offer declined notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'offer_declined'
        )
    
    @staticmethod
    def send_payment_failed(buyer_id):
        """Send payment failed notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'payment_failed'
        )
    
    @staticmethod
    def _extract_user_friendly_error(error_message, error_code, moyasar_response, language='en'):
        """
        Extract and translate Moyasar error into user-friendly message
        
        Returns:
            tuple: (user_friendly_message, should_show_code)
        """
        # First, extract raw error message if not provided
        raw_message = error_message or ''
        raw_code = error_code or ''
        
        if moyasar_response:
            # Extract from transaction
            if 'transaction' in moyasar_response:
                transaction = moyasar_response.get('transaction', {})
                raw_message = transaction.get('message') or raw_message
                raw_code = transaction.get('code') or raw_code
            
            # Extract from source (card errors)
            if 'source' in moyasar_response:
                source = moyasar_response.get('source', {})
                if 'message' in source:
                    raw_message = source.get('message') or raw_message
                if 'transaction' in source:
                    source_transaction = source.get('transaction', {})
                    raw_message = source_transaction.get('message') or raw_message
                    raw_code = source_transaction.get('code') or raw_code
            
            # Extract from top level
            if not raw_message:
                raw_message = (
                    moyasar_response.get('message') or 
                    moyasar_response.get('error') or 
                    moyasar_response.get('description') or
                    moyasar_response.get('error_message') or
                    ''
                )
        
        # Normalize error message for matching (lowercase, remove extra spaces)
        normalized_message = raw_message.lower().strip() if raw_message else ''
        normalized_code = str(raw_code).upper().strip() if raw_code else ''
        
        # Map common payment errors to user-friendly messages
        error_mappings = {
            'en': {
                # Insufficient funds
                'insufficient': 'Insufficient funds in your account',
                'insufficient_funds': 'Insufficient funds in your account',
                'insufficient balance': 'Insufficient balance in your account',
                'insufficient_funds_in_account': 'Insufficient funds in your account',
                '51': 'Insufficient funds in your account',
                '61': 'Insufficient funds in your account',
                
                # Card declined
                'declined': 'Your card was declined by the bank',
                'card_declined': 'Your card was declined by the bank',
                'transaction_declined': 'Your transaction was declined by the bank',
                '05': 'Your card was declined by the bank',
                '14': 'Your card was declined by the bank',
                
                # Invalid card information
                'invalid': 'Invalid card information provided',
                'invalid_card': 'Invalid card information provided',
                'invalid_card_number': 'Invalid card number',
                'invalid_cvv': 'Invalid CVV code',
                'invalid_expiry': 'Invalid card expiry date',
                'invalid_card_data': 'Invalid card information provided',
                '14': 'Invalid card number',
                '54': 'Invalid card expiry date',
                
                # Expired card
                'expired': 'Your card has expired',
                'card_expired': 'Your card has expired',
                'expired_card': 'Your card has expired',
                '33': 'Your card has expired',
                
                # 3DS authentication
                '3ds': '3D Secure authentication failed',
                '3d_secure': '3D Secure authentication failed',
                'authentication_failed': 'Card authentication failed',
                'authentication_required': 'Card authentication is required',
                
                # Card not supported
                'not_supported': 'This card type is not supported',
                'card_not_supported': 'This card type is not supported',
                'unsupported_card': 'This card type is not supported',
                
                # Security/Blocked
                'blocked': 'Your card has been blocked',
                'security': 'Transaction blocked for security reasons',
                'fraud': 'Transaction declined due to security concerns',
                'suspicious': 'Transaction declined due to security concerns',
                
                # Limit exceeded
                'limit': 'Transaction limit exceeded',
                'exceeded': 'Transaction limit exceeded',
                'daily_limit': 'Daily transaction limit exceeded',
                
                # Generic
                'generic': 'Payment could not be processed. Please check your card details and try again',
            },
            'ar': {
                # Insufficient funds
                'insufficient': 'رصيد غير كافٍ في حسابك',
                'insufficient_funds': 'رصيد غير كافٍ في حسابك',
                'insufficient balance': 'رصيد غير كافٍ في حسابك',
                'insufficient_funds_in_account': 'رصيد غير كافٍ في حسابك',
                '51': 'رصيد غير كافٍ في حسابك',
                '61': 'رصيد غير كافٍ في حسابك',
                
                # Card declined
                'declined': 'تم رفض بطاقتك من قبل البنك',
                'card_declined': 'تم رفض بطاقتك من قبل البنك',
                'transaction_declined': 'تم رفض المعاملة من قبل البنك',
                '05': 'تم رفض بطاقتك من قبل البنك',
                '14': 'تم رفض بطاقتك من قبل البنك',
                
                # Invalid card information
                'invalid': 'معلومات البطاقة غير صحيحة',
                'invalid_card': 'معلومات البطاقة غير صحيحة',
                'invalid_card_number': 'رقم البطاقة غير صحيح',
                'invalid_cvv': 'رمز CVV غير صحيح',
                'invalid_expiry': 'تاريخ انتهاء البطاقة غير صحيح',
                'invalid_card_data': 'معلومات البطاقة غير صحيحة',
                '14': 'رقم البطاقة غير صحيح',
                '54': 'تاريخ انتهاء البطاقة غير صحيح',
                
                # Expired card
                'expired': 'بطاقتك منتهية الصلاحية',
                'card_expired': 'بطاقتك منتهية الصلاحية',
                'expired_card': 'بطاقتك منتهية الصلاحية',
                '33': 'بطاقتك منتهية الصلاحية',
                
                # 3DS authentication
                '3ds': 'فشل التحقق من البطاقة',
                '3d_secure': 'فشل التحقق من البطاقة',
                'authentication_failed': 'فشل التحقق من البطاقة',
                'authentication_required': 'التحقق من البطاقة مطلوب',
                
                # Card not supported
                'not_supported': 'نوع البطاقة غير مدعوم',
                'card_not_supported': 'نوع البطاقة غير مدعوم',
                'unsupported_card': 'نوع البطاقة غير مدعوم',
                
                # Security/Blocked
                'blocked': 'بطاقتك محظورة',
                'security': 'تم حظر المعاملة لأسباب أمنية',
                'fraud': 'تم رفض المعاملة لأسباب أمنية',
                'suspicious': 'تم رفض المعاملة لأسباب أمنية',
                
                # Limit exceeded
                'limit': 'تم تجاوز حد المعاملة',
                'exceeded': 'تم تجاوز حد المعاملة',
                'daily_limit': 'تم تجاوز الحد اليومي للمعاملات',
                
                # Generic
                'generic': 'لم يتم معالجة الدفع. يرجى التحقق من تفاصيل بطاقتك والمحاولة مرة أخرى',
            }
        }
        
        mappings = error_mappings.get(language, error_mappings['en'])
        
        # Try to match error message or code
        user_friendly_message = None
        
        # Check error code first (more reliable)
        if normalized_code and normalized_code in mappings:
            user_friendly_message = mappings[normalized_code]
        
        # Check error message keywords
        if not user_friendly_message:
            for key, message in mappings.items():
                if key in normalized_message:
                    user_friendly_message = message
                    break
        
        # If no match found, use generic message
        if not user_friendly_message:
            user_friendly_message = mappings.get('generic', 'Payment could not be processed. Please try again.')
        
        return user_friendly_message, False  # Don't show technical error code to users
    
    @staticmethod
    def send_payment_failed_with_details(buyer_id, error_message=None, error_code=None, moyasar_response=None):
        """
        Send payment failed notification with user-friendly error information from Moyasar
        
        Args:
            buyer_id: Buyer user ID
            error_message: Error message from Moyasar
            error_code: Error code from Moyasar
            moyasar_response: Full Moyasar payment response for extracting error details
        """
        try:
            # Get user
            user = User.objects(id=buyer_id).first()
            if not user:
                print(f"Warning: User not found with id={buyer_id}")
                return None
            
            # Get user's language preference
            user_language = getattr(user, 'language', 'en')
            if user_language not in ['en', 'ar']:
                user_language = 'en'
            
            # Extract user-friendly error message
            user_friendly_message, show_code = NotificationHelper._extract_user_friendly_error(
                error_message, error_code, moyasar_response, user_language
            )
            
            # Build error details message
            if user_language == 'ar':
                error_details = f"<br><br><strong>السبب:</strong> {user_friendly_message}"
            else:
                error_details = f"<br><br><strong>Reason:</strong> {user_friendly_message}"
            
            # Get base template
            template = get_notification_template('buyer', 'payment_failed', user_language)
            if not template:
                print(f"Warning: Template not found for payment_failed")
                return None
            
            # Enhance message with error details
            enhanced_message = template['message'] + error_details
            
            # Create user notification
            user_notification = UserNotification(
                user_id=user.id,
                title=template['title'],
                message=enhanced_message,
                notification_type=template['type'],
                delivered_at=datetime.utcnow()
            )
            user_notification.save()
            
            # Send via WebSocket
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{user.id}',
                        {
                            'type': 'send_notification',
                            'notification': {
                                'id': str(user_notification.id),
                                'title': user_notification.title,
                                'message': user_notification.message,
                                'type': user_notification.notification_type,
                                'createdAt': user_notification.created_at.isoformat()
                            }
                        }
                    )
            except Exception as e:
                print(f"Warning: Failed to send WebSocket notification: {str(e)}")
            
            # Send email notification with error details
            try:
                if hasattr(user, 'email') and user.email:
                    user_name = None
                    if hasattr(user, 'name') and user.name:
                        user_name = user.name
                    elif hasattr(user, 'username') and user.username:
                        user_name = user.username
                    elif hasattr(user, 'first_name') and user.first_name:
                        user_name = user.first_name
                    
                    send_notification_email(
                        email=user.email,
                        notification_title=template['title'],
                        notification_message=enhanced_message,
                        notification_type='error',
                        user_name=user_name,
                        language=user_language
                    )
            except Exception as e:
                print(f"Warning: Failed to send payment failed email: {str(e)}")
            
            return user_notification
        except Exception as e:
            print(f"Error sending payment failed notification with details: {str(e)}")
            return None
    
    @staticmethod
    def send_review_your_purchase(buyer_id):
        """Send review your purchase notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'review_your_purchase'
        )
    
    @staticmethod
    def send_buyer_bank_payment_setup_completed(buyer_id):
        """Send bank/payment setup completed notification to buyer"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'bank_payment_setup_completed'
        )
    
    # AFFILIATE Notifications
    @staticmethod
    def send_welcome_to_affiliate_program(affiliate_id):
        """Send welcome to affiliate program notification"""
        return NotificationHelper.send_notification_to_user(
            affiliate_id, 'affiliate', 'welcome_to_affiliate_program', 'affiliate'
        )
    
    @staticmethod
    def send_affiliate_payment_details_needed(affiliate_id):
        """Send affiliate payment details needed notification"""
        return NotificationHelper.send_notification_to_user(
            affiliate_id, 'affiliate', 'affiliate_payment_details_needed', 'affiliate'
        )
    
    @staticmethod
    def send_affiliate_payment_details_updated(affiliate_id):
        """Send affiliate payment details updated notification"""
        return NotificationHelper.send_notification_to_user(
            affiliate_id, 'affiliate', 'payment_details_updated', 'affiliate'
        )
    
    @staticmethod
    def send_commission_earned(affiliate_id):
        """Send commission earned notification"""
        return NotificationHelper.send_notification_to_user(
            affiliate_id, 'affiliate', 'commission_earned', 'affiliate'
        )
    
    @staticmethod
    def send_commission_approved(affiliate_id):
        """Send commission approved notification"""
        return NotificationHelper.send_notification_to_user(
            affiliate_id, 'affiliate', 'commission_approved', 'affiliate'
        )
    
    @staticmethod
    def send_affiliate_account_suspended(affiliate_id):
        """Send affiliate account suspended notification"""
        return NotificationHelper.send_notification_to_user(
            affiliate_id, 'affiliate', 'affiliate_account_suspended', 'affiliate'
        )

