"""
Notification Templates
Modernized notification messages for all user actions
Supports English (en) and Arabic (ar) languages
Edit this file to customize notification templates
"""

# SELLER Notifications
SELLER_NOTIFICATIONS = {
    'seller_verification_approved': {
        'en': {
            'title': 'Seller Verification Approved',
            'message': 'Your seller verification has been approved. You can now list products and receive payments on the platform.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم اعتماد التحقق من البائع',
            'message': 'تم اعتماد التحقق من البائع الخاص بك. يمكنك الآن إدراج المنتجات واستلام المدفوعات على المنصة.',
            'type': 'seller_message'
        }
    },
    'bank_payment_setup_completed': {
        'en': {
            'title': 'Payment Setup Completed',
            'message': 'Your payout method has been successfully added. You will now receive payments to your registered bank account.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'اكتمال إعداد الدفع',
            'message': 'تمت إضافة طريقة الدفع الخاصة بك بنجاح. ستتلقى الآن المدفوعات في حسابك المصرفي المسجل.',
            'type': 'seller_message'
        }
    },
    'listing_published': {
        'en': {
            'title': 'Listing Published',
            'message': 'Your listing has been published successfully and is now live on the platform.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم نشر القائمة',
            'message': 'تم نشر قائمتك بنجاح وهي الآن متاحة على المنصة.',
            'type': 'seller_message'
        }
    },
    'item_sold': {
        'en': {
            'title': 'Item Sold! 🎉',
            'message': 'Congratulations! Your item has been sold. Please prepare the order for shipment.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم بيع العنصر! 🎉',
            'message': 'تهانينا! تم بيع العنصر الخاص بك. يرجى تحضير الطلب للشحن.',
            'type': 'seller_message'
        }
    },
    'payment_confirmed': {
        'en': {
            'title': 'Payment Confirmed',
            'message': 'Payment for your order has been confirmed. You may proceed with shipping the product.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم تأكيد الدفع',
            'message': 'تم تأكيد الدفع لطلبك. يمكنك المتابعة بشحن المنتج.',
            'type': 'seller_message'
        }
    },
    'order_needs_shipping': {
        'en': {
            'title': 'Order Needs to Be Shipped',
            'message': 'Your order is awaiting shipment. Please ship the item within the required timeframe.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'الطلب يحتاج إلى الشحن',
            'message': 'طلبك في انتظار الشحن. يرجى شحن العنصر خلال الإطار الزمني المطلوب.',
            'type': 'seller_message'
        }
    },
    'buyer_rejected_order': {
        'en': {
            'title': 'Order Rejected',
            'message': 'The buyer has rejected the order.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم رفض الطلب',
            'message': 'رفض المشتري الطلب.',
            'type': 'seller_message'
        }
    },
    'buyer_confirmed_delivery': {
        'en': {
            'title': 'Delivery Confirmed',
            'message': 'The buyer has confirmed receiving the item. Your payout will now be processed within 5-10 business days.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم تأكيد التسليم',
            'message': 'أكد المشتري استلام العنصر. سيتم الآن معالجة دفعتك خلال 5-10 أيام عمل.',
            'type': 'seller_message'
        }
    },
    'new_offer_received': {
        'en': {
            'title': 'New Offer Received',
            'message': 'A buyer has submitted a new offer. Review and accept, decline, or counter the offer.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم استلام عرض جديد',
            'message': 'قدم المشتري عرضًا جديدًا. راجع وقبل أو ارفض أو قدم عرضًا مضادًا.',
            'type': 'seller_message'
        }
    },
    'counter_offer_received': {
        'en': {
            'title': 'Counter-Offer Received',
            'message': 'A buyer has submitted a counter-offer. Please kindly respond before the offer expires.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم استلام عرض مضاد',
            'message': 'قدم المشتري عرضًا مضادًا. يرجى الرد قبل انتهاء صلاحية العرض.',
            'type': 'seller_message'
        }
    },
    'dispute_resolved': {
        'en': {
            'title': 'Dispute Resolved',
            'message': 'A return or dispute has been resolved. Please check the final outcome in your dashboard.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم حل النزاع',
            'message': 'تم حل الإرجاع أو النزاع. يرجى التحقق من النتيجة النهائية في لوحة التحكم الخاصة بك.',
            'type': 'seller_message'
        }
    },
    'payout_sent': {
        'en': {
            'title': 'Payout Sent',
            'message': 'Your payout has been processed and sent to your registered bank account.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تم إرسال الدفعة',
            'message': 'تمت معالجة دفعتك وإرسالها إلى حسابك المصرفي المسجل.',
            'type': 'seller_message'
        }
    },
    'payout_failed': {
        'en': {
            'title': 'Payout Failed',
            'message': 'We could not process your payout. Please update your bank details to receive funds.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'فشل الدفع',
            'message': 'لم نتمكن من معالجة دفعتك. يرجى تحديث تفاصيل حسابك المصرفي لاستلام الأموال.',
            'type': 'seller_message'
        }
    },
    'policy_violation_warning': {
        'en': {
            'title': 'Policy Violation Warning',
            'message': 'Your account has violated platform policies. Continued violations may result in suspension.',
            'type': 'seller_message'
        },
        'ar': {
            'title': 'تحذير من انتهاك السياسة',
            'message': 'انتهك حسابك سياسات المنصة. قد يؤدي الاستمرار في الانتهاكات إلى التعليق.',
            'type': 'seller_message'
        }
    }
}

# BUYER Notifications
BUYER_NOTIFICATIONS = {
    'otp_verification': {
        'en': {
            'title': 'Your OTP Code',
            'message': 'Your OTP code is: {otp_code}. This code will expire in 5 minutes. If you didn\'t request this code, please ignore this email.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'رمز التحقق الخاص بك',
            'message': 'رمز التحقق الخاص بك هو: {otp_code}. سينتهي صلاحية هذا الرمز خلال 5 دقائق. إذا لم تطلب هذا الرمز، يرجى تجاهل هذا البريد الإلكتروني.',
            'type': 'buyer_message'
        }
    },
    'welcome_email': {
        'en': {
            'title': 'Welcome! 👋',
            'message': 'Welcome to our marketplace! Your account has been created successfully.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'مرحباً! 👋',
            'message': 'مرحباً بك في سوقنا! تم إنشاء حسابك بنجاح.',
            'type': 'buyer_message'
        }
    },
    'order_confirmation': {
        'en': {
            'title': 'Order Confirmed',
            'message': 'Thank you for your purchase! Your order has been successfully placed.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم تأكيد الطلب',
            'message': 'شكراً لك على شرائك! تم تقديم طلبك بنجاح.',
            'type': 'buyer_message'
        }
    },
    'payment_successful': {
        'en': {
            'title': 'Payment Successful',
            'message': 'We have received your payment. The seller will now prepare your order.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم الدفع بنجاح',
            'message': 'لقد استلمنا دفعتك. سيقوم البائع الآن بإعداد طلبك.',
            'type': 'buyer_message'
        }
    },
    'seller_shipped_item': {
        'en': {
            'title': 'Item Shipped',
            'message': 'Good news! The seller has shipped your item.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم شحن العنصر',
            'message': 'أخبار جيدة! قام البائع بشحن العنصر الخاص بك.',
            'type': 'buyer_message'
        }
    },
    'item_delivered': {
        'en': {
            'title': 'Item Delivered',
            'message': 'Your item has been marked as delivered. If everything is good, please review the seller.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم تسليم العنصر',
            'message': 'تم وضع علامة على العنصر الخاص بك كمسلم. إذا كان كل شيء جيداً، يرجى مراجعة البائع.',
            'type': 'buyer_message'
        }
    },
    'order_canceled': {
        'en': {
            'title': 'Order Canceled',
            'message': 'Your order has been canceled. Any applicable refunds will be processed shortly.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم إلغاء الطلب',
            'message': 'تم إلغاء طلبك. سيتم معالجة أي استرداد مستحق قريباً.',
            'type': 'buyer_message'
        }
    },
    'offer_accepted': {
        'en': {
            'title': 'Offer Accepted',
            'message': 'Your offer has been accepted. Please proceed with payment to complete the purchase.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم قبول العرض',
            'message': 'تم قبول عرضك. يرجى المتابعة بالدفع لإكمال الشراء.',
            'type': 'buyer_message'
        }
    },
    'offer_declined': {
        'en': {
            'title': 'Offer Declined',
            'message': 'Your offer was declined by the seller.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم رفض العرض',
            'message': 'رفض البائع عرضك.',
            'type': 'buyer_message'
        }
    },
    'counter_offer_received': {
        'en': {
            'title': 'Counter-Offer Received',
            'message': 'The seller has sent a counter-offer. Review and respond before it expires.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم استلام عرض مضاد',
            'message': 'أرسل البائع عرضًا مضادًا. راجع ورد قبل انتهاء صلاحيته.',
            'type': 'buyer_message'
        }
    },
    'dispute_resolved': {
        'en': {
            'title': 'Dispute Resolved',
            'message': 'Your dispute has been resolved. View the final decision in your account.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'تم حل النزاع',
            'message': 'تم حل نزاعك. عرض القرار النهائي في حسابك.',
            'type': 'buyer_message'
        }
    },
    'payment_failed': {
        'en': {
            'title': 'Payment Failed',
            'message': 'Your payment could not be completed. Please try again using a different method.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'فشل الدفع',
            'message': 'لم يتم إكمال دفعتك. يرجى المحاولة مرة أخرى باستخدام طريقة مختلفة.',
            'type': 'buyer_message'
        }
    },
    'review_your_purchase': {
        'en': {
            'title': 'Review Your Purchase',
            'message': 'How was your experience? Please leave a review for the seller.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'راجع مشترياتك',
            'message': 'كيف كانت تجربتك؟ يرجى ترك مراجعة للبائع.',
            'type': 'buyer_message'
        }
    },
    'bank_payment_setup_completed': {
        'en': {
            'title': 'Payment Setup Completed',
            'message': 'Your payment method has been successfully added.',
            'type': 'buyer_message'
        },
        'ar': {
            'title': 'اكتمال إعداد الدفع',
            'message': 'تمت إضافة طريقة الدفع الخاصة بك بنجاح.',
            'type': 'buyer_message'
        }
    }
}

# AFFILIATE Notifications
AFFILIATE_NOTIFICATIONS = {
    'welcome_to_affiliate_program': {
        'en': {
            'title': 'Welcome to Affiliate Program',
            'message': 'Welcome! Your affiliate account is active. Your affiliate code is: <strong style="font-size: 20px; color: #1f2937; letter-spacing: 2px;">{affiliate_code}</strong><br><br><strong>How to Use Your Affiliate Code:</strong><br>1. Share your affiliate code with potential customers<br>2. When they use your code during checkout, you earn a commission<br>3. Track your earnings and referrals in your affiliate dashboard<br>4. Request cashouts when you reach the minimum payout threshold<br><br>Your referral link format: <code>https://dolabb.com?ref={affiliate_code}</code>',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'مرحباً بك في برنامج الشراكة',
            'message': 'مرحباً! حساب الشراكة الخاص بك نشط. رمز الشراكة الخاص بك هو: <strong style="font-size: 20px; color: #1f2937; letter-spacing: 2px;">{affiliate_code}</strong><br><br><strong>كيفية استخدام رمز الشراكة الخاص بك:</strong><br>1. شارك رمز الشراكة الخاص بك مع العملاء المحتملين<br>2. عند استخدامهم لرمزك أثناء الدفع، ستحصل على عمولة<br>3. تتبع أرباحك وإحالاتك في لوحة تحكم الشراكة<br>4. اطلب السحب عند الوصول إلى الحد الأدنى للدفع<br><br>صيغة رابط الإحالة الخاص بك: <code>https://dolabb.com?ref={affiliate_code}</code>',
            'type': 'affiliate_message'
        }
    },
    'affiliate_payment_details_needed': {
        'en': {
            'title': 'Payment Details Needed',
            'message': 'Please add your payout details to receive commission payments.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'تفاصيل الدفع مطلوبة',
            'message': 'يرجى إضافة تفاصيل الدفع الخاصة بك لاستلام مدفوعات العمولة.',
            'type': 'affiliate_message'
        }
    },
    'payment_details_updated': {
        'en': {
            'title': 'Payment Details Updated',
            'message': 'Your payout details have been successfully updated.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'تم تحديث تفاصيل الدفع',
            'message': 'تم تحديث تفاصيل الدفع الخاصة بك بنجاح.',
            'type': 'affiliate_message'
        }
    },
    'commission_earned': {
        'en': {
            'title': 'Commission Earned',
            'message': 'Good job! You earned a commission from one of your referrals.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'تم كسب العمولة',
            'message': 'عمل رائع! لقد ربحت عمولة من إحدى إحالاتك.',
            'type': 'affiliate_message'
        }
    },
    'commission_approved': {
        'en': {
            'title': 'Commission Approved',
            'message': 'Your commission has been approved and added to your earnings.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'تم اعتماد العمولة',
            'message': 'تم اعتماد عمولتك وإضافتها إلى أرباحك.',
            'type': 'affiliate_message'
        }
    },
    'affiliate_payout_sent': {
        'en': {
            'title': 'Payout Sent',
            'message': 'Your affiliate payout has been processed and sent to your registered payment method.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'تم إرسال الدفعة',
            'message': 'تمت معالجة دفعة الشراكة الخاصة بك وإرسالها إلى طريقة الدفع المسجلة.',
            'type': 'affiliate_message'
        }
    },
    'affiliate_payout_failed': {
        'en': {
            'title': 'Payout Failed',
            'message': 'We could not process your affiliate payout. Please update your payment method.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'فشل الدفع',
            'message': 'لم نتمكن من معالجة دفعة الشراكة الخاصة بك. يرجى تحديث طريقة الدفع الخاصة بك.',
            'type': 'affiliate_message'
        }
    },
    'affiliate_policy_violation': {
        'en': {
            'title': 'Policy Violation',
            'message': 'Your affiliate account has violated program guidelines. Please review the policy.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'انتهاك السياسة',
            'message': 'انتهك حساب الشراكة الخاص بك إرشادات البرنامج. يرجى مراجعة السياسة.',
            'type': 'affiliate_message'
        }
    },
    'affiliate_account_suspended': {
        'en': {
            'title': 'Account Suspended',
            'message': 'Your affiliate account has been suspended due to repeated violations.',
            'type': 'affiliate_message'
        },
        'ar': {
            'title': 'تم تعليق الحساب',
            'message': 'تم تعليق حساب الشراكة الخاص بك بسبب الانتهاكات المتكررة.',
            'type': 'affiliate_message'
        }
    }
}

# Helper function to get notification template
def get_notification_template(category, key, language='en'):
    """
    Get notification template by category, key, and language
    
    Args:
        category: 'seller', 'buyer', or 'affiliate'
        key: notification key (e.g., 'item_sold', 'order_confirmation')
        language: 'en' or 'ar' (default: 'en')
    
    Returns:
        dict with 'title', 'message', and 'type' or None if not found
    """
    # Validate language, default to 'en' if invalid
    if language not in ['en', 'ar']:
        language = 'en'
    
    templates = {
        'seller': SELLER_NOTIFICATIONS,
        'buyer': BUYER_NOTIFICATIONS,
        'affiliate': AFFILIATE_NOTIFICATIONS
    }
    
    category_templates = templates.get(category.lower())
    if not category_templates:
        return None
    
    template = category_templates.get(key)
    if not template:
        return None
    
    # Return the language-specific template, fallback to 'en' if language not available
    return template.get(language, template.get('en'))
