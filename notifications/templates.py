"""
Notification Templates
Modernized notification messages for all user actions
Edit this file to customize notification templates
"""

# SELLER Notifications
SELLER_NOTIFICATIONS = {
    'seller_verification_approved': {
        'title': 'Seller Verification Approved',
        'message': 'Your seller verification has been approved. You can now list products and receive payments on the platform.',
        'type': 'seller_message'
    },
    'bank_payment_setup_completed': {
        'title': 'Payment Setup Completed',
        'message': 'Your payout method has been successfully added. You will now receive payments to your registered bank account.',
        'type': 'seller_message'
    },
    'listing_published': {
        'title': 'Listing Published',
        'message': 'Your listing has been published successfully and is now live on the platform.',
        'type': 'seller_message'
    },
    'item_sold': {
        'title': 'Item Sold! 🎉',
        'message': 'Congratulations! Your item has been sold. Please prepare the order for shipment.',
        'type': 'seller_message'
    },
    'payment_confirmed': {
        'title': 'Payment Confirmed',
        'message': 'Payment for your order has been confirmed. You may proceed with shipping the product.',
        'type': 'seller_message'
    },
    'order_needs_shipping': {
        'title': 'Order Needs to Be Shipped',
        'message': 'Your order is awaiting shipment. Please ship the item within the required timeframe.',
        'type': 'seller_message'
    },
    'buyer_rejected_order': {
        'title': 'Order Rejected',
        'message': 'The buyer has rejected the order.',
        'type': 'seller_message'
    },
    'buyer_confirmed_delivery': {
        'title': 'Delivery Confirmed',
        'message': 'The buyer has confirmed receiving the item. Your payout will now be processed within 5-10 business days.',
        'type': 'seller_message'
    },
    'new_offer_received': {
        'title': 'New Offer Received',
        'message': 'A buyer has submitted a new offer. Review and accept, decline, or counter the offer.',
        'type': 'seller_message'
    },
    'counter_offer_received': {
        'title': 'Counter-Offer Received',
        'message': 'A buyer has submitted a counter-offer. Please kindly respond before the offer expires.',
        'type': 'seller_message'
    },
    'dispute_resolved': {
        'title': 'Dispute Resolved',
        'message': 'A return or dispute has been resolved. Please check the final outcome in your dashboard.',
        'type': 'seller_message'
    },
    'payout_sent': {
        'title': 'Payout Sent',
        'message': 'Your payout has been processed and sent to your registered bank account.',
        'type': 'seller_message'
    },
    'payout_failed': {
        'title': 'Payout Failed',
        'message': 'We could not process your payout. Please update your bank details to receive funds.',
        'type': 'seller_message'
    },
    'policy_violation_warning': {
        'title': 'Policy Violation Warning',
        'message': 'Your account has violated platform policies. Continued violations may result in suspension.',
        'type': 'seller_message'
    }
}

# BUYER Notifications
BUYER_NOTIFICATIONS = {
    'otp_verification': {
        'title': 'Your OTP Code',
        'message': 'Your OTP code is: {otp_code}. This code will expire in 5 minutes. If you didn\'t request this code, please ignore this email.',
        'type': 'buyer_message'
    },
    'welcome_email': {
        'title': 'Welcome! 👋',
        'message': 'Welcome to our marketplace! Your account has been created successfully.',
        'type': 'buyer_message'
    },
    'order_confirmation': {
        'title': 'Order Confirmed',
        'message': 'Thank you for your purchase! Your order has been successfully placed.',
        'type': 'buyer_message'
    },
    'payment_successful': {
        'title': 'Payment Successful',
        'message': 'We have received your payment. The seller will now prepare your order.',
        'type': 'buyer_message'
    },
    'seller_shipped_item': {
        'title': 'Item Shipped',
        'message': 'Good news! The seller has shipped your item.',
        'type': 'buyer_message'
    },
    'item_delivered': {
        'title': 'Item Delivered',
        'message': 'Your item has been marked as delivered. If everything is good, please review the seller.',
        'type': 'buyer_message'
    },
    'order_canceled': {
        'title': 'Order Canceled',
        'message': 'Your order has been canceled. Any applicable refunds will be processed shortly.',
        'type': 'buyer_message'
    },
    'offer_accepted': {
        'title': 'Offer Accepted',
        'message': 'Your offer has been accepted. Please proceed with payment to complete the purchase.',
        'type': 'buyer_message'
    },
    'offer_declined': {
        'title': 'Offer Declined',
        'message': 'Your offer was declined by the seller.',
        'type': 'buyer_message'
    },
    'counter_offer_received': {
        'title': 'Counter-Offer Received',
        'message': 'The seller has sent a counter-offer. Review and respond before it expires.',
        'type': 'buyer_message'
    },
    'dispute_resolved': {
        'title': 'Dispute Resolved',
        'message': 'Your dispute has been resolved. View the final decision in your account.',
        'type': 'buyer_message'
    },
    'payment_failed': {
        'title': 'Payment Failed',
        'message': 'Your payment could not be completed. Please try again using a different method.',
        'type': 'buyer_message'
    },
    'review_your_purchase': {
        'title': 'Review Your Purchase',
        'message': 'How was your experience? Please leave a review for the seller.',
        'type': 'buyer_message'
    },
    'bank_payment_setup_completed': {
        'title': 'Payment Setup Completed',
        'message': 'Your payment method has been successfully added.',
        'type': 'buyer_message'
    }
}

# AFFILIATE Notifications
AFFILIATE_NOTIFICATIONS = {
    'welcome_to_affiliate_program': {
        'title': 'Welcome to Affiliate Program',
        'message': 'Welcome! Your affiliate account is active. Your referral link and code are ready to use.',
        'type': 'affiliate_message'
    },
    'affiliate_payment_details_needed': {
        'title': 'Payment Details Needed',
        'message': 'Please add your payout details to receive commission payments.',
        'type': 'affiliate_message'
    },
    'payment_details_updated': {
        'title': 'Payment Details Updated',
        'message': 'Your payout details have been successfully updated.',
        'type': 'affiliate_message'
    },
    'commission_earned': {
        'title': 'Commission Earned',
        'message': 'Good job! You earned a commission from one of your referrals.',
        'type': 'affiliate_message'
    },
    'commission_approved': {
        'title': 'Commission Approved',
        'message': 'Your commission has been approved and added to your earnings.',
        'type': 'affiliate_message'
    },
    'affiliate_payout_sent': {
        'title': 'Payout Sent',
        'message': 'Your affiliate payout has been processed and sent to your registered payment method.',
        'type': 'affiliate_message'
    },
    'affiliate_payout_failed': {
        'title': 'Payout Failed',
        'message': 'We could not process your affiliate payout. Please update your payment method.',
        'type': 'affiliate_message'
    },
    'affiliate_policy_violation': {
        'title': 'Policy Violation',
        'message': 'Your affiliate account has violated program guidelines. Please review the policy.',
        'type': 'affiliate_message'
    },
    'affiliate_account_suspended': {
        'title': 'Account Suspended',
        'message': 'Your affiliate account has been suspended due to repeated violations.',
        'type': 'affiliate_message'
    }
}

# Helper function to get notification template
def get_notification_template(category, key):
    """
    Get notification template by category and key
    
    Args:
        category: 'seller', 'buyer', or 'affiliate'
        key: notification key (e.g., 'item_sold', 'order_confirmation')
    
    Returns:
        dict with 'title', 'message', and 'type' or None if not found
    """
    templates = {
        'seller': SELLER_NOTIFICATIONS,
        'buyer': BUYER_NOTIFICATIONS,
        'affiliate': AFFILIATE_NOTIFICATIONS
    }
    
    category_templates = templates.get(category.lower())
    if not category_templates:
        return None
    
    return category_templates.get(key)

