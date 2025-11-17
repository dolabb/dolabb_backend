"""
Payment models using mongoengine
"""
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField, DictField
from datetime import datetime
from authentication.models import User
from products.models import Order


class Payment(Document):
    """Payment model"""
    order_id = ReferenceField(Order, required=True)
    buyer_id = ReferenceField(User, required=True)
    amount = FloatField(required=True)
    currency = StringField(default='SAR', max_length=10)
    payment_method = StringField(max_length=50)
    moyasar_payment_id = StringField()
    status = StringField(choices=['pending', 'completed', 'failed', 'refunded'], default='pending')
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'payments',
        'indexes': ['order_id', 'buyer_id', 'status', 'created_at']
    }

