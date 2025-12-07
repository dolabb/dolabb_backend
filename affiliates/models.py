"""
Affiliate models using mongoengine
"""
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField, IntField, DictField
from datetime import datetime
from authentication.models import Affiliate, User
from products.models import Order


class AffiliateTransaction(Document):
    """Affiliate transaction model"""
    affiliate_id = ReferenceField(Affiliate, required=True)
    affiliate_name = StringField()
    referred_user_id = ReferenceField(User)
    referred_user_name = StringField()
    transaction_id = ReferenceField(Order)
    commission_rate = FloatField(default=0.0)
    commission_amount = FloatField(default=0.0)
    currency = StringField(default='SAR', max_length=10)  # Currency of the commission
    status = StringField(choices=['pending', 'paid'], default='pending')
    date = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'affiliate_transactions',
        'indexes': ['affiliate_id', 'status', 'date', 'currency']
    }


class AffiliatePayoutRequest(Document):
    """Affiliate payout request model"""
    affiliate_id = ReferenceField(Affiliate, required=True)
    affiliate_name = StringField()
    amount = FloatField(required=True)
    currency = StringField(default='SAR', max_length=10)  # Currency of the payout request
    requested_date = DateTimeField(default=datetime.utcnow)
    payment_method = StringField(choices=['Bank Transfer', 'PayPal', 'Crypto'], default='Bank Transfer')
    status = StringField(choices=['pending', 'approved', 'rejected'], default='pending')
    account_details = StringField()
    rejection_reason = StringField()
    reviewed_at = DateTimeField()
    reviewed_by = StringField()
    
    meta = {
        'collection': 'affiliate_payout_requests',
        'indexes': ['affiliate_id', 'status', 'requested_date', 'currency']
    }

