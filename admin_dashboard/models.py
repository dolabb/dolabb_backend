"""
Admin Dashboard models using mongoengine
"""
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField, IntField, EmbeddedDocument, EmbeddedDocumentField, ListField
from datetime import datetime
from authentication.models import User, Affiliate
from products.models import Product, Order, Offer


class FeeSettings(Document):
    """Fee settings model"""
    dolabb_fee_percentage = FloatField(default=5.0)
    transaction_fee_fixed = FloatField(default=0.0)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'fee_settings',
    }


class CashoutRequest(Document):
    """Cashout request model"""
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    amount = FloatField(required=True)
    requested_date = DateTimeField(default=datetime.utcnow)
    status = StringField(choices=['pending', 'approved', 'rejected'], default='pending')
    account_details = StringField()
    rejection_reason = StringField()
    reviewed_at = DateTimeField()
    reviewed_by = StringField()
    
    meta = {
        'collection': 'cashout_requests',
        'indexes': ['seller_id', 'status', 'requested_date']
    }


class Dispute(Document):
    """Dispute model"""
    case_number = StringField(required=True, unique=True)
    dispute_type = StringField(choices=['product_quality', 'delivery_issue', 'payment_dispute'], required=True)
    buyer_id = ReferenceField(User, required=True)
    buyer_name = StringField()
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    item_id = ReferenceField(Product, required=True)
    item_title = StringField()
    description = StringField()
    status = StringField(choices=['open', 'resolved', 'closed'], default='open')
    admin_notes = StringField()
    resolution = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'disputes',
        'indexes': ['case_number', 'status', 'created_at']
    }


class ActivityLog(Document):
    """Activity log model"""
    activity_type = StringField(required=True)
    details = StringField()
    date = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'activity_logs',
        'indexes': ['date', 'activity_type']
    }

