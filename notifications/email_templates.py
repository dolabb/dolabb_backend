"""
HTML Email Templates for Notifications
Professional styled email templates with logo, banner, and social icons
"""
from django.conf import settings


# Email configuration (you can customize these)
EMAIL_CONFIG = {
    'logo_url': 'https://www.dolabb.com/media/uploads/profiles/a7150ccb-1a9e-4002-b6f5-314b0e8225c2.png',  # Update with your logo URL
    'company_name': 'Dolabb',
    'company_url': 'https://dolabb.com/',  # Update with your website URL
    'support_email': 'support@dolabb.com',
    'social_links': {
        'instagram': 'https://www.instagram.com/dolabb.buy.sell.style',
        'tiktok': 'https://www.tiktok.com/@dolabb.buy.sell.style'
    },
    'app_store_url': 'https://apps.apple.com/app/dolabb',  # Update with your App Store URL
    'play_store_url': 'https://play.google.com/store/apps/details?id=com.dolabb',  # Update with your Play Store URL
    'app_store_logo': 'https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us?size=250x83&releaseDate=1276560000',
    'play_store_logo': 'https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png'
}


def get_email_base_template(title, content, user_name=None, footer_text=None):
    """
    Generate a professional HTML email template
    
    Args:
        title: Email title/heading
        content: Main email content (HTML or text)
        user_name: Optional user name for personalized greeting
        footer_text: Optional custom footer text
    
    Returns:
        Complete HTML email template
    """
    config = EMAIL_CONFIG
    
    # Personalized greeting
    greeting = f"Hi {user_name}," if user_name else "Hi,"
    
    # Social icons HTML
    social_icons = ""
    if config['social_links']:
        social_icons = '<tr><td align="center" style="padding: 20px 0 0;"><table border="0" cellspacing="0" cellpadding="0"><tr>'
        
        if config['social_links'].get('instagram'):
            social_icons += f'''
                        <td style="padding: 0 12px;">
                            <a href="{config['social_links']['instagram']}" target="_blank" style="display: inline-block; text-decoration: none;">
                                <img src="https://www.dolabb.com/media/uploads/profiles/f7dd5ad8-fa19-4d95-8d91-9e66901a5222.jpg" 
                                     alt="Instagram" width="28" height="28" 
                                     style="width: 28px; height: 28px; display: block; border: 0;">
                            </a>
                        </td>'''
        if config['social_links'].get('tiktok'):
            social_icons += f'''
                        <td style="padding: 0 12px;">
                            <a href="{config['social_links']['tiktok']}" target="_blank" style="display: inline-block; text-decoration: none;">
                                <img src="https://www.dolabb.com/media/uploads/profiles/82ae391e-8406-4f50-9b5f-4bde607be746.jpg" 
                                     alt="TikTok" width="28" height="28" 
                                     style="width: 28px; height: 28px; display: block; border: 0;">
                            </a>
                        </td>'''
        
        social_icons += '</tr></table></td></tr>'
    
    # Footer text
    footer_content = footer_text or f"Thanks from the {config['company_name']} team!"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #ffffff;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #ffffff; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="background-color: #ffffff; max-width: 600px; border: 1px solid #e5e7eb; border-radius: 8px;">
                        <!-- Logo at Top -->
                        <tr>
                            <td align="center" style="padding: 50px 40px 30px; background-color: #ffffff; border-radius: 12px 12px 0 0;">
                                <img src="{config['logo_url']}" 
                                     alt="{config['company_name']} Logo" 
                                     width="140" 
                                     height="auto" 
                                     style="max-width: 140px; height: auto; display: block;">
                            </td>
                        </tr>
                        
                        <!-- Greeting -->
                        <tr>
                            <td align="left" style="padding: 0 50px 25px; background-color: #ffffff;">
                                <h1 style="margin: 0; color: #111827; font-size: 28px; font-weight: 700; line-height: 1.2; letter-spacing: -0.5px;">
                                    {greeting}
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content Section -->
                        <tr>
                            <td align="left" style="padding: 0 50px 40px; background-color: #ffffff;">
                                <div style="color: #374151; font-size: 16px; line-height: 1.7; text-align: left;">
                                    {content}
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Social Icons -->
                        {social_icons}
                        
                        <!-- Divider -->
                        <tr>
                            <td align="center" style="padding: 30px 50px 20px; background-color: #ffffff;">
                                <div style="height: 1px; background-color: #e5e7eb; width: 100%;"></div>
                            </td>
                        </tr>
                        
                        <!-- Footer Message -->
                        <tr>
                            <td align="center" style="padding: 0 50px 40px; background-color: #ffffff; border-radius: 0 0 12px 12px;">
                                <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
                                    {footer_content}
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html_template


def render_notification_email(notification_title, notification_message, notification_type='info', 
                             user_name=None, custom_footer=None):
    """
    Render a notification email with professional styling
    
    Args:
        notification_title: Notification title
        notification_message: Notification message (can be HTML or plain text)
        notification_type: Type of notification ('info', 'success', 'warning', 'error')
        user_name: Optional user name for personalized greeting
        custom_footer: Optional custom footer text
    
    Returns:
        Complete HTML email template
    """
    # Convert plain text to HTML if needed
    if not notification_message.startswith('<'):
        # Convert line breaks to <br> tags
        notification_message = notification_message.replace('\n', '<br>')
        # Wrap in paragraph
        notification_message = f'<p style="margin: 0 0 15px;">{notification_message}</p>'
    
    # Icons removed as requested
    
    return get_email_base_template(
        title=notification_title,
        content=notification_message,
        user_name=user_name,
        footer_text=custom_footer
    )


def send_notification_email(email, notification_title, notification_message, notification_type='info',
                           user_name=None, custom_footer=None):
    """
    Send a styled notification email via Resend
    
    Args:
        email: Recipient email address
        notification_title: Email subject/title
        notification_message: Email content
        notification_type: Type of notification
        user_name: Optional user name for personalized greeting
        custom_footer: Optional custom footer text
    
    Returns:
        Resend email response
    """
    try:
        import resend
        from django.conf import settings
        
        # Set API key
        resend.api_key = settings.RESEND_API_KEY
        
        # Generate HTML email
        html_content = render_notification_email(
            notification_title=notification_title,
            notification_message=notification_message,
            notification_type=notification_type,
            user_name=user_name,
            custom_footer=custom_footer
        )
        
        # Send via Resend
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [email],
            "subject": notification_title,
            "html": html_content
        }
        
        email_response = resend.Emails.send(params)
        return email_response
        
    except Exception as e:
        import logging
        logging.error(f"Error sending notification email: {str(e)}")
        raise Exception(f"Failed to send notification email: {str(e)}")

