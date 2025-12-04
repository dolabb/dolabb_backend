# Email Design Guide

## Unified Email Design

All notification emails use the **same consistent design** including:

- Welcome emails
- Order confirmations
- Payment notifications
- Shipping updates
- All other notification types

## Design Features

### ✅ Consistent Elements

1. **Logo at Top** - Company logo centered at the top
2. **Personalized Greeting** - "Hi [User Name]," when user name is available
3. **Centered Content** - All text and content is centered
4. **White Background** - Clean white background throughout
5. **Social Icons** - Instagram, TikTok, and other social links
6. **App Store Badges** - App Store and Google Play download badges
7. **Thanks Message** - "Thanks from the Dolabb team!" footer

### Email Template Structure

```
┌─────────────────────────────────────┐
│         Company Logo                │
│      (150px width, centered)        │
├─────────────────────────────────────┤
│         Hi [User Name],             │
│      (24px font, centered)          │
├─────────────────────────────────────┤
│      Notification Content           │
│   (16px font, centered, with icon) │
├─────────────────────────────────────┤
│      Social Media Icons             │
│   (20px icons, centered row)        │
├─────────────────────────────────────┤
│   App Store | Google Play           │
│   (110px × 36px badges, centered)   │
├─────────────────────────────────────┤
│   Thanks from the Dolabb team!      │
│      (16px font, centered)          │
└─────────────────────────────────────┘
```

## Welcome Email

The welcome email uses the **exact same design** as all other notifications:

- ✅ Same logo placement
- ✅ Same greeting format: "Hi [User Name],"
- ✅ Same centered layout
- ✅ Same footer with social links and app badges
- ✅ Same white background design

### Welcome Email Example

When a user verifies their OTP, they receive a welcome email with:

1. **Logo** at the top
2. **Greeting**: "Hi [User Name],"
3. **Message**: "Welcome to our marketplace! Your account has been created
   successfully."
4. **Social Icons** row
5. **App Store badges**
6. **Thanks message**

## All Emails Use Same Template

All emails are generated using the same base template function:

```python
get_email_base_template(
    title=notification_title,
    content=notification_message,
    user_name=user_name,  # Personalized greeting
    footer_text=custom_footer
)
```

This ensures:

- ✅ Consistent branding
- ✅ Same layout and spacing
- ✅ Same design elements
- ✅ Same user experience

## Customization

To customize the design for ALL emails, edit:

**File:** `notifications/email_templates.py`

**Function:** `get_email_base_template()`

Changes here will apply to:

- Welcome emails
- Order confirmations
- Payment notifications
- Shipping updates
- All other notification emails

## Email Configuration

All email settings are in `EMAIL_CONFIG`:

```python
EMAIL_CONFIG = {
    'logo_url': '...',           # Logo used in all emails
    'company_name': 'Dolabb',    # Company name in footer
    'social_links': {...},       # Social icons in all emails
    'app_store_url': '...',      # App Store badge
    'play_store_url': '...',     # Play Store badge
}
```

## Personalization

All emails support personalization:

- **User Name**: Automatically included in greeting when available
- **Custom Footer**: Can be customized per notification
- **Notification Type**: Icons change based on type (success ✅, error ❌, etc.)

## Testing

To test the email design:

1. **Email sending is automatically enabled** - all notifications send emails
   via Resend
2. **Send a test notification**:

   ```python
   from notifications.email_templates import send_notification_email

   send_notification_email(
       email='test@example.com',
       notification_title='Welcome! 👋',
       notification_message='Welcome to our marketplace!',
       notification_type='info',
       user_name='Test User'
   )
   ```

3. **Check email client** to verify design

## Design Specifications

- **Max Width**: 600px
- **Background**: #ffffff (white)
- **Font Family**: System fonts (Apple, Segoe UI, Roboto)
- **Logo Size**: 150px width (top)
- **Social Icons**: 20px × 20px, 60% opacity
- **App Badges**: 110px × 36px (App Store), 125px × 36px (Play Store)
- **Text Alignment**: Center
- **Padding**: Consistent 40px horizontal, variable vertical

## Responsive Design

The email template is responsive and works on:

- ✅ Desktop email clients (Gmail, Outlook, Apple Mail)
- ✅ Mobile email clients (iOS Mail, Gmail Mobile)
- ✅ Webmail clients (Gmail Web, Outlook Web)

---

**All emails share the same beautiful, consistent design!** 🎨
