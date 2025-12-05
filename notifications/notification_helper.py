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
    def send_notification_to_user(user_id, category, template_key, user_type='user'):
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
            
            # Create user notification
            user_notification = UserNotification(
                user_id=user.id,
                title=template['title'],
                message=template['message'],
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
                        notification_message=template['message'],
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
    def send_order_confirmation(buyer_id):
        """Send order confirmation notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'order_confirmation'
        )
    
    @staticmethod
    def send_payment_successful(buyer_id):
        """Send payment successful notification"""
        return NotificationHelper.send_notification_to_user(
            buyer_id, 'buyer', 'payment_successful'
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

