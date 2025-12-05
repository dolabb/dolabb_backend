"""
Email service using Resend
"""
from notifications.email_templates import send_notification_email
from notifications.templates import get_notification_template
from django.conf import settings


def send_otp_email(email, otp_code, name, language='en'):
    """Send OTP email via Resend using notification template
    
    Args:
        email: Recipient email address
        otp_code: OTP code to send
        name: User's name
        language: Language code ('en' or 'ar'), defaults to 'en'
    """
    try:
        # Validate email parameters
        if not email or not email.strip():
            raise ValueError("Recipient email address is required")
        
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == 'your_resend_api_key_here':
            raise ValueError(
                "Resend API key is not configured. Please set RESEND_API_KEY environment variable. "
                "Current value appears to be a placeholder."
            )
        
        if not settings.RESEND_FROM_EMAIL or settings.RESEND_FROM_EMAIL in ['noreply@yourdomain.com', 'onboarding@resend.dev']:
            raise ValueError(
                f"Resend FROM email is not properly configured. Current value: {settings.RESEND_FROM_EMAIL}. "
                "Please set RESEND_FROM_EMAIL to a verified domain email (e.g., no-reply@dolabb.com)"
            )
        
        # Validate language, default to 'en' if invalid
        if language not in ['en', 'ar']:
            language = 'en'
        
        # Get OTP template with language
        template = get_notification_template('buyer', 'otp_verification', language)
        if not template:
            raise ValueError("OTP email template not found")
        
        # Format message with OTP code
        message = template['message'].format(otp_code=f'<strong style="font-size: 24px; color: #1f2937; letter-spacing: 4px;">{otp_code}</strong>')
        
        # Footer text based on language
        if language == 'ar':
            footer_text = "إذا لم تطلب هذا الرمز، يرجى تجاهل هذا البريد الإلكتروني."
        else:
            footer_text = "If you didn't request this code, please ignore this email."
        
        # Send using notification email system
        email_response = send_notification_email(
            email=email,
            notification_title=template['title'],
            notification_message=message,
            notification_type='info',
            user_name=name,
            custom_footer=footer_text,
            language=language
        )
        
        return email_response
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email: {error_msg}")
        
        # Provide helpful error messages based on common Resend errors
        if "testing emails" in error_msg.lower() or "your own email address" in error_msg.lower():
            raise Exception(
                f"Email sending failed: {error_msg}\n\n"
                "This error usually means:\n"
                "1. You're using a test API key (only allows sending to account owner's email)\n"
                "2. Your domain (dolabb.com) is not verified in Resend\n"
                "3. The FROM email address doesn't match your verified domain\n\n"
                "Solutions:\n"
                "- Verify your domain in Resend dashboard: https://resend.com/domains\n"
                "- Ensure RESEND_FROM_EMAIL is set to an email using your verified domain (e.g., no-reply@dolabb.com)\n"
                "- Use a production API key from your Resend account\n"
                "- Check DNS records are properly configured (see RESEND_DNS_SETUP_GUIDE.md)"
            )
        else:
            raise Exception(f"Failed to send OTP email: {error_msg}")

