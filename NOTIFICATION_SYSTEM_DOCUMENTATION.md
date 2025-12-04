# Notification System Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Email Template Design](#email-template-design)
4. [How Notifications Work](#how-notifications-work)
5. [Notification Types](#notification-types)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Customization](#customization)

---

## Overview

The notification system is a comprehensive solution for sending real-time
notifications to users via:

- **In-App Notifications** (WebSocket) - Real-time delivery
- **Email Notifications** (Resend API) - **Mandatory**, automatically sent for
  all notifications

The system supports three user types:

- **Buyers** - Regular users purchasing items
- **Sellers** - Users selling items on the platform
- **Affiliates** - Users in the affiliate program

---

## System Architecture

### File Structure

```
notifications/
├── models.py              # Database models (Notification, UserNotification)
├── templates.py           # Notification message templates
├── email_templates.py     # HTML email template generator
├── notification_helper.py # Helper functions for sending notifications
├── services.py            # Notification service classes
├── views.py               # API endpoints
└── urls.py                # URL routing
```

### Components

1. **Notification Models** (`models.py`)

   - `Notification`: Admin-created notifications
   - `UserNotification`: User-specific notifications stored in database

2. **Templates** (`templates.py`)

   - Pre-defined notification messages organized by user type
   - Easy to customize without code changes

3. **Email Templates** (`email_templates.py`)

   - Professional HTML email templates
   - Consistent branding and design
   - Responsive and email client compatible

4. **Notification Helper** (`notification_helper.py`)
   - Helper methods for each notification type
   - Automatic notification sending
   - WebSocket and email integration

---

## Email Template Design

### Design Features

The email template follows a clean, modern design with:

1. **Header Section**

   - Company logo at the top (centered)
   - White background throughout

2. **Greeting Section**

   - Personalized greeting: "Hi [User Name],"
   - Centered text

3. **Content Section**

   - Main notification message
   - Supports HTML or plain text
   - Centered alignment

4. **Footer Section**
   - Social media icons (Instagram, TikTok, etc.)
   - App Store and Google Play badges
   - Thanks message from company team

### Template Structure

```
┌─────────────────────────────┐
│      Company Logo           │
│      (Top Center)            │
├─────────────────────────────┤
│      Hi [User Name],        │
│      (Centered)             │
├─────────────────────────────┤
│      Notification Content   │
│      (Centered)             │
├─────────────────────────────┤
│      Social Icons           │
│      (Centered Row)         │
├─────────────────────────────┤
│   App Store | Play Store    │
│      (Centered)             │
├─────────────────────────────┤
│   Thanks from Team Message  │
│      (Centered)             │
└─────────────────────────────┘
```

### Design Specifications

- **Background**: Pure white (#ffffff)
- **Logo Size**: 150px width (top), responsive
- **Font**: System fonts (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto)
- **Social Icons**: 20px × 20px, 60% opacity
- **App Store Badges**: 110px × 36px (App Store), 125px × 36px (Play Store)
- **Spacing**: Consistent padding throughout
- **Alignment**: All content centered

---

## How Notifications Work

### Notification Flow

```
1. Event Triggered
   ↓
2. NotificationHelper Method Called
   ↓
3. Template Retrieved from templates.py
   ↓
4. UserNotification Created & Saved to Database
   ↓
5. WebSocket Notification Sent (Real-time)
   ↓
6. Email Notification Sent (Mandatory, via Resend)
```

### Step-by-Step Process

#### 1. Event Occurs

When a user action occurs (e.g., order placed, payment confirmed), the system
triggers a notification.

#### 2. Helper Method Called

```python
from notifications.notification_helper import NotificationHelper

# Example: When an item is sold
NotificationHelper.send_item_sold(seller_id)
```

#### 3. Template Lookup

The system looks up the notification template from `templates.py`:

```python
template = get_notification_template('seller', 'item_sold')
# Returns: {
#     'title': 'Item Sold! 🎉',
#     'message': 'Congratulations! Your item has been sold...',
#     'type': 'seller_message'
# }
```

#### 4. Database Storage

A `UserNotification` record is created and saved:

```python
user_notification = UserNotification(
    user_id=user.id,
    title=template['title'],
    message=template['message'],
    notification_type=template['type'],
    delivered_at=datetime.utcnow()
)
user_notification.save()
```

#### 5. WebSocket Delivery

The notification is sent via WebSocket for real-time delivery:

```python
channel_layer.group_send(
    f'notifications_{user.id}',
    {
        'type': 'send_notification',
        'notification': {...}
    }
)
```

#### 6. Email Delivery (Mandatory)

An HTML email is automatically sent via Resend API:

```python
send_notification_email(
    email=user.email,
    notification_title=template['title'],
    notification_message=template['message'],
    notification_type='info',
    user_name=user.name
)
```

---

## Notification Types

### Seller Notifications (14 types)

| Notification Key               | Title                        | Trigger Event                                |
| ------------------------------ | ---------------------------- | -------------------------------------------- |
| `seller_verification_approved` | Seller Verification Approved | User creates listing, role changes to seller |
| `bank_payment_setup_completed` | Payment Setup Completed      | Seller updates bank details in profile       |
| `listing_published`            | Listing Published            | Listing created and approved by admin        |
| `item_sold`                    | Item Sold! 🎉                | Order is created                             |
| `payment_confirmed`            | Payment Confirmed            | Payment status = 'completed'                 |
| `order_needs_shipping`         | Order Needs to Be Shipped    | Payment completed, order ready to ship       |
| `buyer_rejected_order`         | Order Rejected               | Order status = 'cancelled'                   |
| `buyer_confirmed_delivery`     | Delivery Confirmed           | Buyer submits review                         |
| `new_offer_received`           | New Offer Received           | Buyer creates offer                          |
| `counter_offer_received`       | Counter-Offer Received       | Buyer/seller counters offer                  |
| `dispute_resolved`             | Dispute Resolved             | Dispute status = 'resolved'                  |
| `payout_sent`                  | Payout Sent                  | Admin approves cashout                       |
| `payout_failed`                | Payout Failed                | Admin rejects cashout                        |
| `policy_violation_warning`     | Policy Violation Warning     | Admin suspends user                          |

### Buyer Notifications (12 types)

| Notification Key               | Title                   | Trigger Event                     |
| ------------------------------ | ----------------------- | --------------------------------- |
| `welcome_email`                | Welcome! 👋             | User verifies OTP                 |
| `order_confirmation`           | Order Confirmed         | Order is created                  |
| `payment_successful`           | Payment Successful      | Payment status = 'completed'      |
| `seller_shipped_item`          | Item Shipped            | Order status = 'shipped'          |
| `item_delivered`               | Item Delivered          | Item marked as delivered          |
| `order_canceled`               | Order Canceled          | Order is cancelled                |
| `offer_accepted`               | Offer Accepted          | Seller accepts buyer's offer      |
| `offer_declined`               | Offer Declined          | Seller declines offer             |
| `counter_offer_received`       | Counter-Offer Received  | Seller sends counter-offer        |
| `dispute_resolved`             | Dispute Resolved        | Dispute resolved                  |
| `payment_failed`               | Payment Failed          | Payment processing fails          |
| `review_your_purchase`         | Review Your Purchase    | After delivery, prompt for review |
| `bank_payment_setup_completed` | Payment Setup Completed | Payment method added              |

### Affiliate Notifications (9 types)

| Notification Key                   | Title                        | Trigger Event                         |
| ---------------------------------- | ---------------------------- | ------------------------------------- |
| `welcome_to_affiliate_program`     | Welcome to Affiliate Program | Affiliate account activated           |
| `affiliate_payment_details_needed` | Payment Details Needed       | Affiliate needs to add payout details |
| `payment_details_updated`          | Payment Details Updated      | Affiliate updates payout details      |
| `commission_earned`                | Commission Earned            | Commission earned from referral       |
| `commission_approved`              | Commission Approved          | Commission approved and added         |
| `affiliate_payout_sent`            | Payout Sent                  | Affiliate payout processed            |
| `affiliate_payout_failed`          | Payout Failed                | Affiliate payout failed               |
| `affiliate_policy_violation`       | Policy Violation             | Affiliate violates guidelines         |
| `affiliate_account_suspended`      | Account Suspended            | Affiliate account suspended           |

---

## Usage Examples

### Example 1: Send Item Sold Notification

```python
from notifications.notification_helper import NotificationHelper

# When an order is created
seller_id = "507f1f77bcf86cd799439011"
NotificationHelper.send_item_sold(seller_id)
```

**What happens:**

1. Looks up `'item_sold'` template from `SELLER_NOTIFICATIONS`
2. Creates `UserNotification` record
3. Sends WebSocket notification to seller
4. Sends email notification via Resend

### Example 2: Send Welcome Email

```python
from notifications.notification_helper import NotificationHelper

# When user verifies OTP
user_id = "507f1f77bcf86cd799439012"
NotificationHelper.send_welcome_email(user_id)
```

**What happens:**

1. Looks up `'welcome_email'` template from `BUYER_NOTIFICATIONS`
2. Creates `UserNotification` record
3. Sends WebSocket notification
4. Sends welcome email via Resend with personalized greeting

### Example 3: Send Custom Notification

```python
from notifications.notification_helper import NotificationHelper

# Send notification with custom category and key
NotificationHelper.send_notification_to_user(
    user_id="507f1f77bcf86cd799439013",
    category='buyer',
    template_key='order_confirmation',
    user_type='user'
)
```

### Example 4: Send Email Notification Directly

```python
from notifications.email_templates import send_notification_email

# Send email notification
send_notification_email(
    email='user@example.com',
    notification_title='Order Confirmed',
    notification_message='Your order #12345 has been confirmed!',
    notification_type='success',
    user_name='John Doe',
    custom_footer='Thanks for shopping with us!'
)
```

### Example 5: Render Email Template Only

```python
from notifications.email_templates import render_notification_email

# Generate HTML email template
html_content = render_notification_email(
    notification_title='Welcome!',
    notification_message='Welcome to our platform!',
    notification_type='info',
    user_name='Jane Smith'
)

# Use html_content for custom email sending
```

---

## Configuration

### Email Configuration

Edit `EMAIL_CONFIG` in `notifications/email_templates.py`:

```python
EMAIL_CONFIG = {
    'logo_url': 'https://www.dolabb.com/media/uploads/profiles/...',
    'company_name': 'Dolabb',
    'company_url': 'https://dolabb.com/',
    'support_email': 'support@dolabb.com',
    'social_links': {
        'instagram': 'https://www.instagram.com/dolabb.buy.sell.style',
        'tiktok': 'https://www.tiktok.com/@dolabb.buy.sell.style'
    },
    'app_store_url': 'https://apps.apple.com/app/dolabb',
    'play_store_url': 'https://play.google.com/store/apps/details?id=com.dolabb',
    'app_store_logo': 'https://tools.applemediaservices.com/api/badges/...',
    'play_store_logo': 'https://play.google.com/intl/en_us/badges/...'
}
```

### Django Settings

**Required** settings in `settings.py` (Email notifications are mandatory):

```python
# Resend API Configuration (MANDATORY - used for all email notifications including OTP)
RESEND_API_KEY = 'your-resend-api-key'  # Required
RESEND_FROM_EMAIL = 'noreply@dolabb.com'  # Required - must be verified in Resend

# Channels Configuration (for WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### Email Notifications (Mandatory)

Email notifications are **automatically enabled** and sent via Resend API for
all notifications. The system:

1. Automatically sends emails when notifications are created
2. Uses Resend API for reliable email delivery
3. Includes personalized greetings with user names
4. Applies appropriate notification type styling (success, error, warning, info)

**Note:** Ensure `RESEND_API_KEY` and `RESEND_FROM_EMAIL` are properly
configured in Django settings.

---

## Customization

### Customize Notification Messages

Edit `notifications/templates.py`:

```python
SELLER_NOTIFICATIONS = {
    'item_sold': {
        'title': 'Item Sold! 🎉',  # Change title
        'message': 'Your custom message here...',  # Change message
        'type': 'seller_message'
    }
}
```

### Customize Email Template

Edit `notifications/email_templates.py`:

1. **Change Logo**: Update `logo_url` in `EMAIL_CONFIG`
2. **Change Colors**: Modify inline styles in `get_email_base_template()`
3. **Change Layout**: Modify HTML structure in template string
4. **Add Social Links**: Add to `social_links` in `EMAIL_CONFIG`

### Add New Notification Type

1. **Add Template** in `templates.py`:

```python
SELLER_NOTIFICATIONS = {
    'new_notification': {
        'title': 'New Notification Title',
        'message': 'Notification message here',
        'type': 'seller_message'
    }
}
```

2. **Add Helper Method** in `notification_helper.py`:

```python
@staticmethod
def send_new_notification(user_id):
    """Send new notification"""
    return NotificationHelper.send_notification_to_user(
        user_id, 'seller', 'new_notification'
    )
```

3. **Call Helper Method** where needed:

```python
NotificationHelper.send_new_notification(seller_id)
```

---

## Email Template Functions

### `get_email_base_template()`

Generates the base HTML email template.

**Parameters:**

- `title` (str): Email title/subject
- `content` (str): Main email content (HTML or text)
- `user_name` (str, optional): User name for personalized greeting
- `footer_text` (str, optional): Custom footer message

**Returns:** HTML email template string

### `render_notification_email()`

Renders a notification email with styling.

**Parameters:**

- `notification_title` (str): Notification title
- `notification_message` (str): Notification message
- `notification_type` (str): 'info', 'success', 'warning', 'error'
- `user_name` (str, optional): User name
- `custom_footer` (str, optional): Custom footer text

**Returns:** Complete HTML email template

### `send_notification_email()`

Sends a notification email via Resend API.

**Parameters:**

- `email` (str): Recipient email address
- `notification_title` (str): Email subject
- `notification_message` (str): Email content
- `notification_type` (str): Notification type
- `user_name` (str, optional): User name
- `custom_footer` (str, optional): Custom footer

**Returns:** Resend API response

---

## Notification Helper Methods

### Seller Methods

- `send_seller_verification_approved(seller_id)`
- `send_bank_payment_setup_completed(user_id, user_type='user')`
- `send_listing_published(seller_id)`
- `send_item_sold(seller_id)`
- `send_payment_confirmed(seller_id)`
- `send_order_needs_shipping(seller_id)`
- `send_buyer_rejected_order(seller_id)`
- `send_buyer_confirmed_delivery(seller_id)`
- `send_new_offer_received(seller_id)`
- `send_counter_offer_received(user_id, user_role='seller')`
- `send_dispute_resolved(user_id, user_role='seller')`
- `send_payout_sent(user_id, user_type='user')`
- `send_payout_failed(user_id, user_type='user')`
- `send_policy_violation_warning(user_id, user_type='user')`

### Buyer Methods

- `send_welcome_email(user_id)`
- `send_order_confirmation(buyer_id)`
- `send_payment_successful(buyer_id)`
- `send_seller_shipped_item(buyer_id)`
- `send_item_delivered(buyer_id)`
- `send_order_canceled(buyer_id)`
- `send_offer_accepted(buyer_id)`
- `send_offer_declined(buyer_id)`
- `send_payment_failed(buyer_id)`
- `send_review_your_purchase(buyer_id)`
- `send_buyer_bank_payment_setup_completed(buyer_id)`

### Affiliate Methods

- `send_welcome_to_affiliate_program(affiliate_id)`
- `send_affiliate_payment_details_needed(affiliate_id)`
- `send_affiliate_payment_details_updated(affiliate_id)`
- `send_commission_earned(affiliate_id)`
- `send_commission_approved(affiliate_id)`
- `send_affiliate_account_suspended(affiliate_id)`

### Generic Method

- `send_notification_to_user(user_id, category, template_key, user_type='user')`

---

## Best Practices

1. **Always use helper methods** instead of calling
   `send_notification_to_user()` directly
2. **Handle errors gracefully** - notifications should not break the main flow
3. **Test email templates** in different email clients before production
4. **Keep messages concise** - notifications should be clear and actionable
5. **Use appropriate notification types** - helps with filtering and styling
6. **Personalize when possible** - use `user_name` parameter for better
   engagement
7. **Monitor email delivery** - check Resend dashboard for delivery rates

---

## Troubleshooting

### Email Not Sending

1. Check `RESEND_API_KEY` in settings (must be configured)
2. Verify `RESEND_FROM_EMAIL` is verified in Resend dashboard
3. Ensure user has a valid email address
4. Review error logs for exceptions
5. Check Resend dashboard for delivery status

### WebSocket Not Working

1. Verify Redis is running
2. Check `CHANNEL_LAYERS` configuration
3. Ensure WebSocket consumer is properly configured
4. Check browser console for connection errors

### Template Not Found

1. Verify template key exists in `templates.py`
2. Check category matches ('seller', 'buyer', 'affiliate')
3. Ensure template key is spelled correctly

---

## Support

For issues or questions:

- Check error logs in Django console
- Review Resend dashboard for email delivery status
- Verify database records in MongoDB
- Test WebSocket connections

---

**Last Updated:** 2025-01-27 **Version:** 1.0.0
