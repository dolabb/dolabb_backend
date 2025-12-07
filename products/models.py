"""
Product models using mongoengine
"""
from mongoengine import Document, StringField, FloatField, DateTimeField, ListField, ReferenceField, BooleanField, IntField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime
from authentication.models import User, Affiliate


class ShippingInfo(EmbeddedDocument):
    """Shipping information embedded document"""
    cost = FloatField(default=0.0)
    estimated_days = IntField(default=7)
    locations = ListField(StringField())


class Product(Document):
    """Product/Listing model"""
    title = StringField(required=True, max_length=500)
    description = StringField()
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    category = StringField(required=True, choices=['women', 'men', 'watches', 'jewelry', 'accessories'])
    subcategory = StringField(max_length=200)
    brand = StringField(max_length=200)
    price = FloatField(required=True)
    original_price = FloatField()
    currency = StringField(default='SAR', max_length=10)
    quantity = IntField(default=1)
    gender = StringField(max_length=50)
    size = StringField(max_length=50)
    color = StringField(max_length=50)
    condition = StringField(choices=['new', 'like-new', 'good', 'fair'], default='good')
    sku = StringField(max_length=100)
    tags = ListField(StringField())
    images = ListField(StringField())
    status = StringField(choices=['active', 'sold', 'removed'], default='active')
    reviewed = BooleanField(default=False)
    approved = BooleanField(default=False)
    shipping_info = EmbeddedDocumentField(ShippingInfo)
    shipping_cost = FloatField(default=0.0)
    processing_time_days = IntField(default=7)
    affiliate_code = StringField(max_length=50)
    tax_percentage = FloatField(default=None, null=True)  # Tax percentage (e.g., 15.0 for 15%), optional
    likes_count = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'products',
        'indexes': ['seller_id', 'category', 'status', 'created_at', 'title']
    }


class SavedProduct(Document):
    """Saved/Wishlist products"""
    user_id = ReferenceField(User, required=True)
    product_id = ReferenceField(Product, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'saved_products',
        'indexes': ['user_id', 'product_id'],
        'unique_together': [('user_id', 'product_id')]
    }


class Offer(Document):
    """Offer model for product negotiations"""
    product_id = ReferenceField(Product, required=True)
    buyer_id = ReferenceField(User, required=True)
    buyer_name = StringField()
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    offer_amount = FloatField(required=True)
    original_price = FloatField(required=True)
    currency = StringField(default='SAR', max_length=10)  # Currency from product at time of offer
    shipping_cost = FloatField(default=0.0)
    # Shipping address details
    shipping_address = StringField(max_length=500)
    zip_code = StringField(max_length=20)
    house_number = StringField(max_length=50)
    status = StringField(choices=['pending', 'accepted', 'rejected', 'countered', 'expired', 'paid'], default='pending')
    expiration_date = DateTimeField()
    counter_offer_amount = FloatField()
    last_countered_by = StringField(choices=['buyer', 'seller'], default=None, null=True)  # Track who made the last counter
    buyer_counter_count = IntField(default=0, null=True)  # Track how many times buyer has countered
    seller_counter_count = IntField(default=0, null=True)  # Track how many times seller has countered
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'offers',
        'indexes': ['product_id', 'buyer_id', 'seller_id', 'status', 'created_at']
    }


class Order(Document):
    """Order model"""
    order_number = StringField(required=True, unique=True)
    buyer_id = ReferenceField(User, required=True)
    buyer_name = StringField()
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    product_id = ReferenceField(Product, required=True)
    product_title = StringField()
    offer_id = ReferenceField(Offer)
    price = FloatField(required=True)
    offer_price = FloatField()
    currency = StringField(default='SAR', max_length=10)  # Currency from product/offer at time of order
    shipping_cost = FloatField(default=0.0)
    total_price = FloatField(required=True)
    dolabb_fee = FloatField(default=0.0)
    affiliate_code = StringField(max_length=50)  # Affiliate code used in order
    affiliate_commission = FloatField(default=0.0)  # Commission paid to affiliate (25% of platform fee)
    seller_payout = FloatField(default=0.0)  # Amount seller receives after fees
    delivery_address = StringField()
    full_name = StringField()
    phone = StringField()
    city = StringField()
    postal_code = StringField()
    country = StringField()
    additional_info = StringField()
    status = StringField(choices=['pending', 'packed', 'ready', 'shipped', 'delivered', 'cancelled'], default='pending')
    tracking_number = StringField()
    shipment_proof = StringField()  # URL to shipment proof image
    payment_status = StringField(choices=['pending', 'completed', 'failed'], default='pending')
    payment_id = StringField()
    review_submitted = BooleanField(default=False)  # Track if buyer has submitted a review
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'orders',
        'indexes': ['buyer_id', 'seller_id', 'status', 'created_at', 'order_number']
    }


class Review(Document):
    """Review model for product/seller reviews"""
    order_id = ReferenceField(Order, required=True)
    buyer_id = ReferenceField(User, required=True)
    buyer_name = StringField()
    seller_id = ReferenceField(User, required=True)
    seller_name = StringField()
    product_id = ReferenceField(Product, required=True)
    product_title = StringField()
    rating = IntField(required=True, min_value=1, max_value=5)  # 1-5 star rating
    comment = StringField(max_length=1000)  # Review comment
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'reviews',
        'indexes': ['order_id', 'buyer_id', 'seller_id', 'product_id', 'created_at'],
        'unique_together': [('order_id', 'buyer_id')]  # One review per order per buyer
    }

