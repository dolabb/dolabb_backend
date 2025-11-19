"""
Email service using Resend
"""
import resend
from django.conf import settings

# Set API key (validation happens in send_otp_email function)
resend.api_key = settings.RESEND_API_KEY


def send_otp_email(email, otp_code, name):
    """Send OTP email via Resend"""
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
        
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [email],
            "subject": "Your OTP Code",
            "html": f"""
            <html>
            <body>
                <h2>Hello {name},</h2>
                <p>Your OTP code is: <strong>{otp_code}</strong></p>
                <p>This code will expire in 5 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </body>
            </html>
            """
        }
        email_response = resend.Emails.send(params)
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

