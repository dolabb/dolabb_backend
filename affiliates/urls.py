"""
Affiliate URLs
"""
from django.urls import path
from affiliates import views

urlpatterns = [
    path('validate-code/', views.validate_affiliate_code, name='validate_affiliate_code'),
    path('cashout/', views.request_cashout, name='request_cashout'),
    path('cashout-requests/', views.get_my_cashout_requests, name='get_my_cashout_requests'),  # Affiliate's own cashout history
    path('profile/', views.affiliate_profile, name='affiliate_profile'),
    path('bank-details/', views.bank_details, name='bank_details'),  # Separate API for bank details
    path('transactions/', views.get_my_transactions, name='get_my_transactions'),  # Affiliate's own transactions
    path('earnings-breakdown/', views.get_earnings_breakdown, name='get_earnings_breakdown'),  # Time-based earnings breakdown for graphs
    path('all/', views.get_all_affiliates, name='get_all_affiliates'),
    path('<str:affiliate_id>/transactions/', views.get_affiliate_transactions, name='get_affiliate_transactions'),  # Admin: get any affiliate's transactions
    path('<str:affiliate_id>/update-commission/', views.update_commission_rate, name='update_commission_rate'),
    path('<str:affiliate_id>/suspend/', views.suspend_affiliate, name='suspend_affiliate'),
    path('payout-requests/', views.get_payout_requests, name='get_payout_requests'),
    path('payout-requests/<str:payout_id>/approve/', views.approve_payout, name='approve_payout'),
    path('payout-requests/<str:payout_id>/reject/', views.reject_payout, name='reject_payout'),
]

