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
    path('listings/<str:listing_id>/update/', views.update_listing, name='update_listing'),
    
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
    path('disputes/<str:dispute_id>/', views.get_dispute_details, name='get_dispute_details'),
    path('disputes/<str:dispute_id>/update/', views.update_dispute, name='update_dispute'),
    path('disputes/<str:dispute_id>/close/', views.close_dispute, name='close_dispute'),
    path('disputes/<str:dispute_id>/comments/', views.add_dispute_message, name='add_dispute_message'),
    path('disputes/<str:dispute_id>/evidence/', views.upload_dispute_evidence, name='upload_dispute_evidence'),
    
    # User Management - Additional
    path('users/<str:user_id>/', views.get_user_details, name='get_user_details'),
    path('users/<str:user_id>/reactivate/', views.reactivate_user, name='reactivate_user'),
    
    # Transaction Management - Additional
    path('transactions/<str:transaction_id>/', views.get_transaction_details, name='get_transaction_details'),
    
    # Cashout Requests - Additional
    path('cashout-requests/<str:cashout_id>/', views.get_cashout_details, name='get_cashout_details'),
    
    # Dashboard - Additional
    path('dashboard/recent-activities/', views.get_recent_activities, name='get_recent_activities'),
    
    # Fee Settings - Additional
    path('fee-settings/calculate/', views.calculate_fee, name='calculate_fee'),
    
    # General Admin APIs
    path('profile/', views.get_admin_profile, name='get_admin_profile'),
    path('profile/update/', views.update_admin_profile, name='update_admin_profile'),
    path('profile/change-password/', views.change_admin_password, name='change_admin_password'),
    path('activity-logs/', views.get_activity_logs, name='get_activity_logs'),
    
    # Affiliate Management - Additional
    path('affiliates/<str:affiliate_id>/', views.get_affiliate_details, name='get_affiliate_details'),
    path('affiliates/<str:affiliate_id>/toggle-status/', views.toggle_affiliate_status, name='toggle_affiliate_status'),
    
    # Notification Management - Additional
    path('notifications/<str:notification_id>/toggle/', views.toggle_notification_status, name='toggle_notification_status'),
    path('notifications/templates/', views.get_notification_templates, name='get_notification_templates'),
    
    # Hero Section Management
    path('hero-section/', views.get_hero_section, name='get_hero_section'),
    path('hero-section/update/', views.update_hero_section, name='update_hero_section'),
]

