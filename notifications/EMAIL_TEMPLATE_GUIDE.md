# Email Template Customization Guide

## 📧 Email Template System

The email notification system uses **HTML templates** with professional styling, logo, banner, and social icons.

## 📁 Files

1. **`notifications/templates.py`** - Text content for notifications (used for in-app notifications)
2. **`notifications/email_templates.py`** - HTML email templates with styling (used for email notifications)

## 🎨 Customization

### 1. Update Email Configuration

Edit `notifications/email_templates.py` and update the `EMAIL_CONFIG` dictionary:

```python
EMAIL_CONFIG = {
    'logo_url': 'https://yourdomain.com/logo.png',  # Your logo URL
    'company_name': 'Dolabb',
    'company_url': 'https://yourdomain.com',  # Your website
    'support_email': 'support@dolabb.com',
    'social_links': {
        'facebook': 'https://facebook.com/yourpage',
        'twitter': 'https://twitter.com/yourhandle',
        'instagram': 'https://instagram.com/yourhandle',
        'linkedin': 'https://linkedin.com/company/yourcompany'
    }
}
```

### 2. Customize Colors

Edit the color scheme in `get_email_base_template()` function:

```python
# Primary color (buttons, links)
background-color: #4F46E5  # Change to your brand color

# Header gradient
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)  # Change gradient colors
```

### 3. Add Your Logo

1. Upload your logo to your server/CDN
2. Update `logo_url` in `EMAIL_CONFIG`
3. Recommended logo size: 120px width, transparent PNG

### 4. Customize Social Icons

- Add/remove social platforms in `EMAIL_CONFIG['social_links']`
- Icons are automatically generated using Simple Icons
- Icons appear in the footer

### 5. Customize Banner/Header

The banner section can be customized in `get_email_base_template()`:

```python
<!-- Banner/Header Section -->
<tr>
    <td style="padding: 30px 40px; background-color: #ffffff;">
        <h1 style="margin: 0; color: #1f2937; font-size: 28px; font-weight: 700;">
            {title}
        </h1>
    </td>
</tr>
```

## 🚀 Enabling Email Notifications

By default, email notifications are **disabled** (commented out) to avoid sending emails during development.

To enable email notifications:

1. Open `notifications/notification_helper.py`
2. Find the commented email code in `send_notification_to_user()`
3. Uncomment the email sending code:

```python
# Optionally send email notification
try:
    if hasattr(user, 'email') and user.email:
        send_notification_email(
            email=user.email,
            notification_title=template['title'],
            notification_message=template['message'],
            notification_type='info'
        )
except Exception as e:
    print(f"Warning: Failed to send email notification: {str(e)}")
```

## 📝 Adding CTA Buttons

You can add call-to-action buttons to specific notifications:

```python
# In notification_helper.py, when calling send_notification_email:
send_notification_email(
    email=user.email,
    notification_title="Order Confirmed",
    notification_message="Your order has been placed successfully!",
    notification_type='success',
    button_text="View Order",  # Button text
    button_url="https://yourdomain.com/orders/123"  # Button URL
)
```

## 🎯 Notification Types

Different notification types show different icons:

- `'success'` - ✅ Green checkmark
- `'warning'` - ⚠️ Warning icon
- `'error'` - ❌ Error icon
- `'info'` - ℹ️ Info icon

## 📱 Responsive Design

The email templates are responsive and work on:
- Desktop email clients (Gmail, Outlook, Apple Mail)
- Mobile devices
- Webmail clients

## 🔧 Advanced Customization

### Custom Footer Text

```python
send_notification_email(
    email=user.email,
    notification_title="Welcome!",
    notification_message="Thanks for joining!",
    custom_footer="Need help? Contact us anytime!"
)
```

### HTML Content

You can use HTML in notification messages:

```python
notification_message = """
<p>Welcome to our platform!</p>
<ul>
    <li>Feature 1</li>
    <li>Feature 2</li>
</ul>
"""
```

## 📧 Testing Emails

1. Set up Resend API key in your environment
2. Enable email notifications (uncomment code)
3. Trigger a notification action
4. Check your email inbox

## 🎨 Template Structure

```
┌─────────────────────────────┐
│   Header (Logo + Gradient)   │
├─────────────────────────────┤
│   Title/Banner              │
├─────────────────────────────┤
│   Content (Message)         │
├─────────────────────────────┤
│   CTA Button (Optional)     │
├─────────────────────────────┤
│   Social Icons              │
├─────────────────────────────┤
│   Footer                    │
└─────────────────────────────┘
```

## 💡 Tips

1. **Logo**: Use PNG with transparent background, max 120px width
2. **Colors**: Use your brand colors for consistency
3. **Buttons**: Keep button text short (2-3 words)
4. **Content**: Keep messages concise and clear
5. **Testing**: Test on multiple email clients before going live

---

**All email templates are ready to customize!** 🎉

