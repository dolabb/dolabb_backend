"""
Notification models using mongoengine
"""
from mongoengine import Document, StringField, DateTimeField, ReferenceField, BooleanField, DictField
from datetime import datetime
from authentication.models import Admin, User


class Notification(Document):
    """Admin-created notification model"""
    title = StringField(required=True, max_length=200)
    message = StringField(required=True)
    notification_type = StringField(choices=['system_alert', 'buyer_message', 'seller_message', 'affiliate_message'], required=True)
    target_audience = StringField(choices=['all', 'buyers', 'sellers', 'affiliates'], required=True)
    active = BooleanField(default=True)
    created_by = ReferenceField(Admin)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    scheduled_for = DateTimeField()
    variables = DictField()
    
    meta = {
        'collection': 'notifications',
        'indexes': ['target_audience', 'active', 'created_at']
    }


class UserNotification(Document):
    """User notification model"""
    notification_id = ReferenceField(Notification)
    user_id = ReferenceField(User, required=True)
    title = StringField(required=True)
    message = StringField(required=True)
    notification_type = StringField(required=True)
    is_read = BooleanField(default=False)
    delivered_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'user_notifications',
        'indexes': ['user_id', 'is_read', 'created_at']
    }

