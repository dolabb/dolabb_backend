"""
HTML Email Templates for Notifications
Professional styled email templates with logo, banner, and social icons
"""
from django.conf import settings
import html


# Email configuration (you can customize these)
EMAIL_CONFIG = {
    'logo_url': 'https://cdn.dolabb.com/media/uploads/profiles/5dcee68d-4713-4743-8da8-f7cc11fc67b7.png',  # Update with your logo URL
    'company_name': 'Dوُlabb',  # Mixed Arabic/English company name
    'company_url': 'https://dolabb.com/',  # Update with your website URL
    'support_email': 'support@dolabb.com',
    'social_links': {
        'instagram': {
            'url': 'https://www.instagram.com/dolabb.buy.sell.style',
            'icon_url': 'https://cdn.dolabb.com/media/uploads/profiles/a4221f40-57dc-45dd-ad8d-f00b74a2d660.jpg'
        },
        'tiktok': {
            'url': 'https://www.tiktok.com/@dolabb.buy.sell.style',
            'icon_url': 'https://cdn.dolabb.com/media/uploads/profiles/3a790ca8-a900-432a-8a1f-104e0d12fbba.jpg'
        }
    },
    'app_store_url': 'https://apps.apple.com/app/dolabb',  # Update with your App Store URL
    'play_store_url': 'https://play.google.com/store/apps/details?id=com.dolabb',  # Update with your Play Store URL
    'app_store_logo': 'https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us?size=250x83&releaseDate=1276560000',
    'play_store_logo': 'https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png'
}


def get_email_base_template(title, content, user_name=None, footer_text=None, language='en', action_button=None):
    """
    Generate a professional HTML email template
    
    Args:
        title: Email title/heading
        content: Main email content (HTML or text)
        user_name: Optional user name for personalized greeting
        footer_text: Optional custom footer text
        language: Language code ('en' or 'ar') for RTL support
        action_button: Optional dict with 'text', 'url', and optionally 'text_ar' for action button
    
    Returns:
        Complete HTML email template
    """
    config = EMAIL_CONFIG
    
    # Determine if RTL is needed
    is_rtl = language == 'ar'
    text_direction = 'rtl' if is_rtl else 'ltr'
    text_align = 'right' if is_rtl else 'left'
    
    # Personalized greeting based on language
    if is_rtl:
        greeting = f"مرحباً {user_name}،" if user_name else "مرحباً،"
    else:
        greeting = f"Hi {user_name}," if user_name else "Hi,"
    
    # Social icons HTML
    social_icons = ""
    if config['social_links']:
        social_icons = '<tr><td align="center" style="padding: 20px 0 0;"><table role="presentation" border="0" cellspacing="0" cellpadding="0" style="margin: 0 auto;"><tr>'
        
        # Instagram
        instagram = config['social_links'].get('instagram')
        if instagram:
            instagram_url = instagram.get('url') if isinstance(instagram, dict) else instagram
            instagram_icon = instagram.get('icon_url') if isinstance(instagram, dict) else 'https://cdn.dolabb.com/media/uploads/profiles/a4221f40-57dc-45dd-ad8d-f00b74a2d660.jpg'
            social_icons += f'''
                        <td style="padding: 0 12px;">
                            <a href="{instagram_url}" target="_blank" style="display: inline-block; text-decoration: none; border: 0; outline: none;">
                                <img src="{instagram_icon}" 
                                     alt="Instagram" 
                                     width="28" 
                                     height="28" 
                                     border="0"
                                     style="width: 28px; height: 28px; display: block; border: 0; outline: none; text-decoration: none;">
                            </a>
                        </td>'''
        
        # TikTok
        tiktok = config['social_links'].get('tiktok')
        if tiktok:
            tiktok_url = tiktok.get('url') if isinstance(tiktok, dict) else tiktok
            tiktok_icon = tiktok.get('icon_url') if isinstance(tiktok, dict) else 'https://cdn.dolabb.com/media/uploads/profiles/3a790ca8-a900-432a-8a1f-104e0d12fbba.jpg'
            social_icons += f'''
                        <td style="padding: 0 12px;">
                            <a href="{tiktok_url}" target="_blank" style="display: inline-block; text-decoration: none; border: 0; outline: none;">
                                <img src="{tiktok_icon}" 
                                     alt="TikTok" 
                                     width="28" 
                                     height="28" 
                                     border="0"
                                     style="width: 28px; height: 28px; display: block; border: 0; outline: none; text-decoration: none;">
                            </a>
                        </td>'''
        
        social_icons += '</tr></table></td></tr>'
    
    # Footer text based on language
    # Get company name - ensure it's properly handled for mixed Arabic/English
    company_name = config['company_name']
    
    if footer_text:
        footer_content = footer_text
    else:
        if is_rtl:
            footer_content = f"شكراً من فريق {company_name}!"
        else:
            footer_content = f"Thanks from the {company_name} team!"
    
    # Font family for Arabic support
    font_family = "'Segoe UI', 'Tahoma', 'Arial', sans-serif" if is_rtl else "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    
    # Generate action button HTML if provided
    action_button_html = ""
    if action_button and action_button.get('url'):
        button_text = action_button.get('text_ar' if is_rtl else 'text', action_button.get('text', 'Click Here'))
        button_url = action_button.get('url', '#')
        # Escape button text for HTML
        button_text_encoded = html.escape(button_text)
        action_button_html = f"""
                        <tr>
                            <td align="center" style="padding: 0 50px 30px; background-color: #ffffff;">
                                <table role="presentation" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center" style="border-radius: 8px; background-color: #111827;">
                                            <a href="{button_url}" target="_blank" style="display: inline-block; padding: 14px 32px; font-family: {font_family}; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 8px; background-color: #111827; text-align: center;">
                                                {button_text_encoded}
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
        """
    
    # Escape title for HTML (but keep company name as-is to preserve Arabic characters)
    title_encoded = html.escape(title)
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="{language}" dir="{text_direction}">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title_encoded}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: {font_family}; background-color: #ffffff; direction: {text_direction};">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #ffffff; padding: 40px 20px; direction: {text_direction};">
            <tr>
                <td align="center">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="background-color: #ffffff; max-width: 600px; border: 1px solid #e5e7eb; border-radius: 8px; direction: {text_direction};">
                        <!-- Logo at Top -->
                        <tr>
                            <td align="center" style="padding: 50px 40px 30px; background-color: #ffffff; border-radius: 12px 12px 0 0;">
                                <img src="{config['logo_url']}" 
                                     alt="{company_name} Logo" 
                                     width="140" 
                                     border="0" 
                                     style="max-width: 140px; height: auto; display: block; border: 0; outline: none; text-decoration: none;">
                            </td>
                        </tr>
                        
                        <!-- Greeting -->
                        <tr>
                            <td align="{text_align}" style="padding: 0 50px 25px; background-color: #ffffff;">
                                <h1 style="margin: 0; color: #111827; font-size: 28px; font-weight: 700; line-height: 1.2; letter-spacing: -0.5px; text-align: {text_align}; direction: {text_direction};">
                                    {greeting}
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content Section -->
                        <tr>
                            <td align="{text_align}" style="padding: 0 50px 40px; background-color: #ffffff;">
                                <div style="color: #374151; font-size: 16px; line-height: 1.7; text-align: {text_align}; direction: {text_direction};">
                                    {content}
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Action Button Section -->
                        {action_button_html}
                        
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
                             user_name=None, custom_footer=None, language='en', action_button=None):
    """
    Render a notification email with professional styling
    
    Args:
        notification_title: Notification title
        notification_message: Notification message (can be HTML or plain text)
        notification_type: Type of notification ('info', 'success', 'warning', 'error')
        user_name: Optional user name for personalized greeting
        custom_footer: Optional custom footer text
        language: Language code ('en' or 'ar') for RTL support
        action_button: Optional dict with 'text', 'url', and optionally 'text_ar' for action button
    
    Returns:
        Complete HTML email template
    """
    # Convert plain text to HTML if needed
    if not notification_message.startswith('<'):
        # Convert line breaks to <br> tags
        notification_message = notification_message.replace('\n', '<br>')
        # Wrap in paragraph with appropriate direction
        text_align = 'right' if language == 'ar' else 'left'
        text_direction = 'rtl' if language == 'ar' else 'ltr'
        notification_message = f'<p style="margin: 0 0 15px; text-align: {text_align}; direction: {text_direction};">{notification_message}</p>'
    
    # Icons removed as requested
    
    return get_email_base_template(
        title=notification_title,
        content=notification_message,
        user_name=user_name,
        footer_text=custom_footer,
        language=language,
        action_button=action_button
    )


def send_notification_email(email, notification_title, notification_message, notification_type='info',
                           user_name=None, custom_footer=None, language='en', action_button=None):
    """
    Send a styled notification email via Resend
    
    Args:
        email: Recipient email address
        notification_title: Email subject/title
        notification_message: Email content
        notification_type: Type of notification
        user_name: Optional user name for personalized greeting
        custom_footer: Optional custom footer text
        language: Language code ('en' or 'ar') for RTL support
        action_button: Optional dict with 'text', 'url', and optionally 'text_ar' for action button
    
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
            custom_footer=custom_footer,
            language=language,
            action_button=action_button
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

