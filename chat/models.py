"""
Chat models using mongoengine
"""
from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, BooleanField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime
from authentication.models import User
from products.models import Product, Offer


class Message(Document):
    """Chat message model"""
    conversation_id = StringField(required=True)
    sender_id = ReferenceField(User, required=True)
    receiver_id = ReferenceField(User, required=True)
    product_id = ReferenceField(Product)
    text = StringField()
    attachments = ListField(StringField())
    message_type = StringField(choices=['text', 'offer', 'image'], default='text')
    offer_id = ReferenceField(Offer)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'messages',
        'indexes': [
            'conversation_id',
            'sender_id',
            'receiver_id',
            'created_at',
            # Composite indexes for common query patterns
            [('conversation_id', 1), ('created_at', 1)],  # For paginated message retrieval
            [('conversation_id', 1), ('receiver_id', 1), ('is_read', 1)]  # For unread messages query
        ]
    }


class Conversation(Document):
    """Conversation model"""
    participants = ListField(ReferenceField(User), required=True)
    product_id = ReferenceField(Product)
    last_message = StringField()
    last_message_at = DateTimeField()
    unread_count_sender = StringField(default='0')
    unread_count_receiver = StringField(default='0')
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'conversations',
        'indexes': ['participants', 'product_id', 'updated_at']
    }

