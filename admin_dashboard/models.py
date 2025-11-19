"""
Admin Dashboard models using mongoengine
"""
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField, IntField, EmbeddedDocument, EmbeddedDocumentField, ListField
from datetime import datetime
from authentication.models import User, Affiliate
from products.models import Product, Order, Offer


class FeeSettings(Document):
    """Fee settings model"""
    # Platform fee settings
    minimum_fee = FloatField(default=5.0)  # Minimum SAR 5
    fee_percentage = FloatField(default=5.0)  # 5% fee
    threshold_amount_1 = FloatField(default=100.0)  # SAR 100 threshold
    threshold_amount_2 = FloatField(default=2000.0)  # SAR 2000 threshold
    maximum_fee = FloatField(default=100.0)  # Maximum SAR 100 (5% of 2000)
    
    # Transaction fee (if needed separately)
    transaction_fee_fixed = FloatField(default=0.0)
    
    # Default affiliate commission percentage (25% of platform fee)
    default_affiliate_commission_percentage = FloatField(default=25.0)
    
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

