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
    shipping_cost = FloatField(default=0.0)
    status = StringField(choices=['pending', 'accepted', 'rejected', 'countered', 'expired'], default='pending')
    expiration_date = DateTimeField()
    counter_offer_amount = FloatField()
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
    shipping_cost = FloatField(default=0.0)
    total_price = FloatField(required=True)
    dolabb_fee = FloatField(default=0.0)
    delivery_address = StringField()
    full_name = StringField()
    phone = StringField()
    city = StringField()
    postal_code = StringField()
    country = StringField()
    additional_info = StringField()
    status = StringField(choices=['pending', 'ready', 'shipped', 'delivered', 'cancelled'], default='pending')
    tracking_number = StringField()
    payment_status = StringField(choices=['pending', 'completed', 'failed'], default='pending')
    payment_id = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'orders',
        'indexes': ['buyer_id', 'seller_id', 'status', 'created_at', 'order_number']
    }

