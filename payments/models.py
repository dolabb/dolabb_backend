"""
Payment models using mongoengine
"""
from mongoengine import (
    Document,
    StringField,
    FloatField,
    DateTimeField,
    ReferenceField,
    DictField,
    ListField,
)
from datetime import datetime
from authentication.models import User
from products.models import Order


class Payment(Document):
    """
    Payment model

    Notes about multi-order / multi-seller payments:
    - For backward compatibility, `order_id` always points to the "primary" order
      (typically the first seller's order).
    - For cart checkouts with multiple sellers paid in a single Moyasar charge,
      `orders` will contain *all* related orders and `is_group_payment` will be True.
    - Business logic that needs to update all related orders (statuses, payouts, etc.)
      should always iterate over `orders` if present, otherwise fall back to `order_id`.
    """

    # Primary order (for backward compatibility)
    order_id = ReferenceField(Order, required=True)

    # All related orders for this payment (for multi-seller cart payments)
    orders = ListField(ReferenceField(Order))
    is_group_payment = StringField(
        choices=['single', 'group'], default='single'
    )  # simple enum instead of Boolean for easier querying

    buyer_id = ReferenceField(User, required=True)
    amount = FloatField(required=True)
    currency = StringField(default='SAR', max_length=10)
    payment_method = StringField(max_length=50)
    moyasar_payment_id = StringField()
    status = StringField(
        choices=['pending', 'completed', 'failed', 'refunded'], default='pending'
    )
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'payments',
        'indexes': [
            'order_id',
            'buyer_id',
            'status',
            'created_at',
            'moyasar_payment_id',
        ],
    }

