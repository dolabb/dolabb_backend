"""
Admin Dashboard URLs
"""
from django.urls import path
from admin_dashboard import views

urlpatterns = [
    # Dashboard Stats
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/revenue-trends/', views.revenue_trends, name='revenue_trends'),
    path('dashboard/sales-over-time/', views.sales_over_time, name='sales_over_time'),
    path('dashboard/listings-status/', views.listings_status_summary, name='listings_status'),
    path('dashboard/transaction-types/', views.transaction_types_summary, name='transaction_types'),
    path('dashboard/disputes-status/', views.disputes_status, name='disputes_status'),
    path('dashboard/cashout-requests-summary/', views.cashout_requests_summary, name='cashout_requests_summary'),
    
    # User Management
    path('users/', views.get_users, name='get_users'),
    path('users/<str:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('users/<str:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/<str:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Listing Management
    path('listings/', views.get_listings, name='get_listings'),
    path('listings/<str:listing_id>/approve/', views.approve_listing, name='approve_listing'),
    path('listings/<str:listing_id>/reject/', views.reject_listing, name='reject_listing'),
    path('listings/<str:listing_id>/hide/', views.hide_listing, name='hide_listing'),
    
    # Transactions
    path('transactions/', views.get_transactions, name='get_transactions'),
    
    # Cashout Requests
    path('cashout-requests/', views.get_cashout_requests, name='get_cashout_requests'),
    path('cashout-requests/<str:cashout_id>/approve/', views.approve_cashout, name='approve_cashout'),
    path('cashout-requests/<str:cashout_id>/reject/', views.reject_cashout, name='reject_cashout'),
    
    # Fee Settings
    path('fee-settings/', views.get_fee_settings, name='get_fee_settings'),
    path('fee-settings/update/', views.update_fee_settings, name='update_fee_settings'),
    path('fee-settings/summary/', views.fee_collection_summary, name='fee_collection_summary'),
    
    # Disputes
    path('disputes/', views.get_disputes, name='get_disputes'),
    path('disputes/<str:dispute_id>/update/', views.update_dispute, name='update_dispute'),
    path('disputes/<str:dispute_id>/close/', views.close_dispute, name='close_dispute'),
]

