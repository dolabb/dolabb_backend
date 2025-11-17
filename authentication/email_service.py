"""
Email service using Resend
"""
import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY


def send_otp_email(email, otp_code, name):
    """Send OTP email via Resend"""
    try:
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
        print(f"Error sending email: {str(e)}")
        raise Exception(f"Failed to send OTP email: {str(e)}")

