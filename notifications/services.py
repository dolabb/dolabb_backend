"""
Notification services
"""
from datetime import datetime
from notifications.models import Notification, UserNotification
from authentication.models import User, Admin, Affiliate
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class NotificationService:
    """Notification service"""
    
    @staticmethod
    def create_notification(title, message, notification_type, target_audience, admin_id, scheduled_for=None, variables=None):
        """Create notification"""
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            target_audience=target_audience,
            created_by=admin_id,
            scheduled_for=scheduled_for,
            variables=variables or {}
        )
        notification.save()
        
        return notification
    
    @staticmethod
    def send_notification(notification_id):
        """Send notification to target audience"""
        notification = Notification.objects(id=notification_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        # Get target users
        users = []
        if notification.target_audience == 'all':
            users = list(User.objects())
            # Also include affiliates
            affiliates = list(Affiliate.objects())
            # Convert affiliates to user-like objects for notification
        elif notification.target_audience == 'buyers':
            users = list(User.objects(role='buyer'))
        elif notification.target_audience == 'sellers':
            users = list(User.objects(role='seller'))
        elif notification.target_audience == 'affiliates':
            affiliates = list(Affiliate.objects())
            # Handle affiliates separately
        
        # Create user notifications and send via WebSocket
        channel_layer = get_channel_layer()
        
        for user in users:
            user_notification = UserNotification(
                notification_id=notification_id,
                user_id=user.id,
                title=notification.title,
                message=notification.message,
                notification_type=notification.notification_type,
                delivered_at=datetime.utcnow()
            )
            user_notification.save()
            
            # Send via WebSocket
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
        
        return len(users)
    
    @staticmethod
    def get_notifications(user_id, page=1, limit=20, is_read=None):
        """Get user notifications"""
        query = UserNotification.objects(user_id=user_id)
        
        if is_read is not None:
            query = query.filter(is_read=is_read)
        
        total = query.count()
        skip = (page - 1) * limit
        notifications = query.skip(skip).limit(limit).order_by('-created_at')
        
        notifications_list = []
        for notif in notifications:
            notifications_list.append({
                'id': str(notif.id),
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'isRead': notif.is_read,
                'deliveredAt': notif.delivered_at.isoformat() if notif.delivered_at else None,
                'createdAt': notif.created_at.isoformat()
            })
        
        return notifications_list, total
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark notification as read"""
        notification = UserNotification.objects(id=notification_id, user_id=user_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        notification.is_read = True
        notification.save()
        
        return notification
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read"""
        UserNotification.objects(user_id=user_id, is_read=False).update(set__is_read=True)
        return True
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """Delete notification"""
        notification = UserNotification.objects(id=notification_id, user_id=user_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        notification.delete()
        return True
    
    @staticmethod
    def bulk_delete_notifications(user_id, notification_ids):
        """Bulk delete notifications"""
        UserNotification.objects(user_id=user_id, id__in=notification_ids).delete()
        return True
    
    @staticmethod
    def get_admin_notifications(page=1, limit=20, search=None, notification_type=None, date_from=None, date_to=None):
        """Get admin notifications"""
        query = Notification.objects()
        
        if search:
            query = query.filter(title__icontains=search)
        if notification_type:
            query = query.filter(notification_type=notification_type)
        if date_from:
            query = query.filter(created_at__gte=date_from)
        if date_to:
            query = query.filter(created_at__lte=date_to)
        
        total = query.count()
        skip = (page - 1) * limit
        notifications = query.skip(skip).limit(limit).order_by('-created_at')
        
        notifications_list = []
        for notif in notifications:
            notifications_list.append({
                'id': str(notif.id),
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'targetAudience': notif.target_audience,
                'active': notif.active,
                'createdAt': notif.created_at.isoformat(),
                'scheduledFor': notif.scheduled_for.isoformat() if notif.scheduled_for else None
            })
        
        return notifications_list, total
    
    @staticmethod
    def update_notification(notification_id, title=None, message=None, active=None):
        """Update notification"""
        notification = Notification.objects(id=notification_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        if title:
            notification.title = title
        if message:
            notification.message = message
        if active is not None:
            notification.active = active
        
        notification.updated_at = datetime.utcnow()
        notification.save()
        
        return notification
    
    @staticmethod
    def delete_admin_notification(notification_id):
        """Delete admin notification"""
        notification = Notification.objects(id=notification_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        notification.delete()
        return True

