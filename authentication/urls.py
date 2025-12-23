"""
Authentication URLs
"""
from django.urls import path
from authentication import views
from authentication.otp_views import verify_otp, admin_verify_otp, user_verify_otp, affiliate_verify_otp, resend_otp
from authentication.image_views import upload_image, check_vps_config

urlpatterns = [
    # Admin auth
    path('admin/signup/', views.admin_signup, name='admin_signup'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/verify-otp/', admin_verify_otp, name='admin_verify_otp'),
    path('admin/resend-otp/', views.admin_resend_otp, name='admin_resend_otp'),
    path('admin/forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('admin/resend-forgot-password-otp/', views.admin_resend_forgot_password_otp, name='admin_resend_forgot_password_otp'),
    path('admin/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    
    # User auth
    path('signup/', views.user_signup, name='user_signup'),
    path('login/', views.user_login, name='user_login'),
    path('verify-otp/', user_verify_otp, name='user_verify_otp'),
    path('forgot-password/', views.user_forgot_password, name='user_forgot_password'),
    path('reset-password/', views.user_reset_password, name='user_reset_password'),
    path('profile/', views.get_profile, name='get_profile'),  # Handles GET, PATCH, PUT
    path('profile/<str:user_id>/', views.get_user_profile_by_id, name='get_user_profile_by_id'),
    path('profile/update/', views.update_profile, name='update_profile_legacy'),  # Keep for backward compatibility
    path('language/update/', views.update_language, name='update_language'),
    
    # Affiliate auth
    path('affiliate/signup/', views.affiliate_signup, name='affiliate_signup'),
    path('affiliate/login/', views.affiliate_login, name='affiliate_login'),
    path('affiliate/verify-otp/', affiliate_verify_otp, name='affiliate_verify_otp'),
    path('affiliate/forget-password/', views.affiliate_forgot_password, name='affiliate_forgot_password'),
    path('affiliate/reset-password/', views.affiliate_reset_password, name='affiliate_reset_password'),
    
    # Combined OTP Verification (for all user types)
    path('verify-otp-combined/', verify_otp, name='verify_otp_combined'),
    
    # Combined Resend OTP (for all user types)
    path('resend-otp/', resend_otp, name='resend_otp'),
    
    # Image Upload
    path('upload-image/', upload_image, name='upload_image'),
    path('check-vps-config/', check_vps_config, name='check_vps_config'),
]

