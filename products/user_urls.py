"""
User-specific product URLs
"""
from django.urls import path
from products.user_views import (
    get_user_products, get_user_orders, get_user_offers, ship_order
)

urlpatterns = [
    path('products/', get_user_products, name='user_products'),
    path('orders/', get_user_orders, name='user_orders'),
    path('offers/', get_user_offers, name='user_offers'),
    path('payments/', get_user_orders, name='user_payments'),  # Same as orders for seller
    path('payments/<str:order_id>/ship/', ship_order, name='ship_order'),
]

