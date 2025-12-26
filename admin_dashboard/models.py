"""
Admin Dashboard models using mongoengine
"""
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField, IntField, EmbeddedDocument, EmbeddedDocumentField, ListField, BooleanField
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
    """Cashout request model (Seller Payout Request)"""
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    amount = FloatField(required=True)
    payment_method = StringField(choices=['Bank Transfer', 'PayPal', 'Stripe'], default='Bank Transfer')
    requested_date = DateTimeField(default=datetime.utcnow)
    status = StringField(choices=['pending', 'approved', 'rejected'], default='pending')
    account_details = StringField()
    rejection_reason = StringField()
    reviewed_at = DateTimeField()
    reviewed_by = StringField()
    notes = StringField()  # Admin notes
    moyasar_payout_id = StringField()  # Moyasar payout transaction ID
    payout_error = StringField()  # Error message if payout fails
    
    meta = {
        'collection': 'cashout_requests',
        'indexes': ['seller_id', 'status', 'requested_date']
    }


class DisputeMessage(EmbeddedDocument):
    """Dispute message/comment model"""
    message = StringField(required=True)
    sender_type = StringField(choices=['buyer', 'admin'], required=True)
    sender_id = StringField(required=True)
    sender_name = StringField()
    created_at = DateTimeField(default=datetime.utcnow)


class DisputeEvidence(EmbeddedDocument):
    """Dispute evidence/file model"""
    id = StringField(required=True)  # Unique ID for the evidence
    url = StringField(required=True)  # File URL
    filename = StringField(required=True)  # Stored filename
    original_filename = StringField()  # Original filename
    file_type = StringField()  # File type (image, document, etc.)
    content_type = StringField()  # MIME type
    description = StringField()  # Optional description
    uploaded_by = StringField(required=True)  # User ID who uploaded
    uploaded_by_name = StringField()  # Name of uploader
    uploaded_by_type = StringField(choices=['buyer', 'seller', 'admin'], default='buyer')  # Type of uploader
    uploaded_at = DateTimeField(required=True, default=datetime.utcnow)


class Dispute(Document):
    """Dispute model"""
    case_number = StringField(required=True, unique=True)
    dispute_type = StringField(choices=['product_quality', 'delivery_issue', 'payment_dispute'], required=True)
    buyer_id = ReferenceField(User, required=True)
    buyer_name = StringField()
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    order_id = ReferenceField(Order, required=True)
    item_id = ReferenceField(Product, required=True)
    item_title = StringField()
    description = StringField()
    status = StringField(choices=['open', 'resolved', 'closed'], default='open')
    admin_notes = StringField()
    resolution = StringField()
    messages = ListField(EmbeddedDocumentField(DisputeMessage), default=list)
    evidence = ListField(EmbeddedDocumentField(DisputeEvidence), default=list)  # Evidence files
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'disputes',
        'indexes': ['case_number', 'status', 'created_at', 'buyer_id', 'order_id']
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


class HeroSection(Document):
    """Hero section model for homepage"""
    # Background settings
    background_type = StringField(choices=['image', 'single_color', 'gradient'], default='image')
    image_url = StringField()  # URL for background image
    single_color = StringField()  # Hex color code (e.g., '#FF5733')
    gradient_colors = ListField(StringField())  # List of hex colors for gradient (e.g., ['#FF5733', '#33FF57'])
    gradient_direction = StringField(default='to right')  # CSS gradient direction (e.g., 'to right', 'to bottom', '135deg')
    
    # Text content
    title = StringField(required=True)
    subtitle = StringField()
    button_text = StringField()
    button_link = StringField()
    
    # Text styling
    text_color = StringField(default='#FFFFFF')  # Hex color for text
    
    # Status
    is_active = BooleanField(default=True)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'hero_section',
        'indexes': ['is_active', 'updated_at']
    }

