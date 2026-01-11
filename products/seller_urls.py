"""
Seller URLs for earnings and payout management
"""
from django.urls import path
from products.seller_views import (
    get_seller_earnings,
    request_seller_payout,
    get_seller_payout_requests,
    bank_details
)

urlpatterns = [
    path('earnings/', get_seller_earnings, name='seller_earnings'),
    path('payout/request/', request_seller_payout, name='request_seller_payout'),
    path('payout-requests/', get_seller_payout_requests, name='seller_payout_requests'),
    path('bank-details/', bank_details, name='seller_bank_details'),
]

