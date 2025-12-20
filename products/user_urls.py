"""
User-specific product URLs
"""
from django.urls import path
from products.user_views import (
    get_user_products, get_user_orders, get_user_offers, ship_order, update_order_status,
    create_review, get_product_reviews, get_seller_rating, get_seller_reviews, create_dispute,
    get_my_disputes, get_my_dispute_details, add_dispute_comment, get_products_by_seller
)

urlpatterns = [
    path('products/', get_user_products, name='user_products'),
    path('orders/', get_user_orders, name='user_orders'),
    path('offers/', get_user_offers, name='user_offers'),
    path('payments/', get_user_orders, name='user_payments'),  # Same as orders for seller
    path('payments/<str:order_id>/ship/', ship_order, name='ship_order'),
    path('orders/<str:order_id>/status/', update_order_status, name='update_order_status'),
    # Review endpoints
    path('reviews/create/', create_review, name='create_review'),
    path('reviews/product/<str:product_id>/', get_product_reviews, name='get_product_reviews'),
    path('reviews/seller/<str:seller_id>/rating/', get_seller_rating, name='get_seller_rating'),
    path('reviews/seller/<str:seller_id>/', get_seller_reviews, name='get_seller_reviews'),
    # Seller products endpoint (public)
    path('seller/<str:seller_id>/products/', get_products_by_seller, name='get_products_by_seller'),
    # Dispute/Report endpoints - Order matters: more specific routes first
    path('disputes/create/', create_dispute, name='create_dispute'),
    path('disputes/<str:dispute_id>/comments/', add_dispute_comment, name='add_dispute_comment'),
    path('disputes/<str:dispute_id>/', get_my_dispute_details, name='get_my_dispute_details'),
    path('disputes/', get_my_disputes, name='get_my_disputes'),
]

