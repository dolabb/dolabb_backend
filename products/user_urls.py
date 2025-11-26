"""
User-specific product URLs
"""
from django.urls import path
from products.user_views import (
    get_user_products, get_user_orders, get_user_offers, ship_order,
    create_review, get_product_reviews, get_seller_rating, get_seller_reviews, create_dispute
)

urlpatterns = [
    path('products/', get_user_products, name='user_products'),
    path('orders/', get_user_orders, name='user_orders'),
    path('offers/', get_user_offers, name='user_offers'),
    path('payments/', get_user_orders, name='user_payments'),  # Same as orders for seller
    path('payments/<str:order_id>/ship/', ship_order, name='ship_order'),
    # Review endpoints
    path('reviews/create/', create_review, name='create_review'),
    path('reviews/product/<str:product_id>/', get_product_reviews, name='get_product_reviews'),
    path('reviews/seller/<str:seller_id>/rating/', get_seller_rating, name='get_seller_rating'),
    path('reviews/seller/<str:seller_id>/', get_seller_reviews, name='get_seller_reviews'),
    # Dispute/Report endpoints
    path('disputes/create/', create_dispute, name='create_dispute'),
]

