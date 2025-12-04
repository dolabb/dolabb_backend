# Notification Implementation Plan

## Analysis Summary

Based on `Notifications_text.md` and codebase review, here's the mapping of
notifications to existing features:

---

## ✅ SELLER Notifications - Feature Mapping

### Account & Verification

1. **Seller Verification Approved** ❓

   - **Status**: NOT FOUND in codebase
   - **Question**: Is there a seller verification process? Where is it handled?

   Answer:when buyer created any listing and its role chnaged to seller then send this notification

2. **Bank / Payment Setup Completed** ❓

   - **Status**: NOT FOUND in codebase
   - **Question**: Where do sellers add bank/payment details? Is this during
     signup or separate?
     Answer:add optional fields while updating profile for seller or buyer bank details and when users update that recive this notifications

3. **Bank / Payment Setup Needs Attention** ❓
   - **Status**: NOT FOUND in codebase
   - **Question**: When should this trigger? If seller skips bank setup during
     signup?
    Answer:remove this  
### Listing Management

4. **Listing Published** ✅
   - **Feature**: `admin_dashboard/services.py` -
     `ListingManagementService.approve_listing()`
   - **Location**: `admin_dashboard/views.py` - `approve_listing()`
   - **Action**: When admin approves listing, `listing.approved = True`
  Addition: also when seller added listing on success of that created listing send this mail too
### Orders & Sales

5. **Item Sold** ✅

   - **Feature**: `products/services.py` - `OrderService.create_order()`
   - **Location**: `payments/views.py` - `checkout()`
   - **Action**: When order is created

6. **Payment Confirmed** ✅

   - **Feature**: `payments/services.py` -
     `MoyasarPaymentService.process_payment()`
   - **Location**: `payments/views.py` - `process_payment()`
   - **Action**: When `payment.status = 'completed'` and
     `order.payment_status = 'completed'`

7. **Order Needs to Be Shipped** ✅

   - **Feature**: Order status tracking
   - **Location**: Order status is `'packed'` after payment
   - **Action**: Could trigger when order status is `'packed'` or `'ready'`

8. **Shipping Label Ready** ❓

   - **Status**: NOT FOUND in codebase
   - **Question**: Is there a shipping label generation feature? Or should this
     be removed?
  Answer: skip this
9. **Buyer reject Order** ✅

   - **Feature**: Order can be cancelled
   - **Location**: Order status can be `'cancelled'`
   - **Action**: When order status changes to `'cancelled'`

10. **Buyer Confirmed Delivery** ✅
    - **Feature**: `products/user_views.py` - `create_review()`
    - **Location**: `products/services.py` - `ReviewService.create_review()`
    - **Action**: When buyer submits review (`order.review_submitted = True`)

### Offers

11. **New Offer Received** ✅

    - **Feature**: `products/services.py` - `OfferService.create_offer()`
    - **Location**: `products/offer_views.py` - `create_offer()`
    - **Action**: When buyer creates offer

12. **Counter‑Offer Received** ✅
    - **Feature**: `products/services.py` - `OfferService.counter_offer()`
    - **Location**: `products/offer_views.py` - `counter_offer()`
    - **Action**: When buyer/seller counters offer

### Returns & Disputes

13. **Return / Dispute Resolved** ✅
    - **Feature**: `admin_dashboard/services.py` -
      `DisputeService.resolve_dispute()`
    - **Location**: Admin dashboard
    - **Action**: When dispute status changes to `'resolved'`

### Payments & Earnings

14. **Payout Sent** ✅

    - **Feature**: `admin_dashboard/services.py` -
      `CashoutService.approve_cashout()`
    - **Location**: `admin_dashboard/views.py` - Admin approves payout
    - **Action**: When `cashout.status = 'approved'`

15. **Payout Failed** ✅
    - **Feature**: `admin_dashboard/services.py` -
      `CashoutService.reject_cashout()`
    - **Location**: `admin_dashboard/views.py` - Admin rejects payout
    - **Action**: When `cashout.status = 'rejected'`

### Platform & Safety

16. **Policy Violation Warning** ❓
    - **Status**: NOT FOUND in codebase
    - **Question**: Is there a policy violation system? How should this be
      triggered?
  Answer: when admin suspend any user
---

## ✅ BUYER Notifications - Feature Mapping

### Account & Security

17. **Welcome Email** ✅
    - **Feature**: `authentication/services.py` -
      `AuthService.user_verify_otp()`
    - **Location**: `authentication/otp_views.py` - `verify_otp()`
    - **Action**: When user account is created (after OTP verification)

### Orders & Purchases

18. **Order Confirmation** ✅

    - **Feature**: `products/services.py` - `OrderService.create_order()`
    - **Location**: `payments/views.py` - `checkout()`
    - **Action**: When order is created

19. **Payment Successful** ✅

    - **Feature**: `payments/services.py` -
      `MoyasarPaymentService.process_payment()`
    - **Location**: `payments/views.py` - `process_payment()`
    - **Action**: When `payment.status = 'completed'`

20. **Seller Shipped Item** ✅

    - **Feature**: `products/services.py` - `OrderService.update_order_status()`
    - **Location**: `products/user_views.py` - `ship_order()`
    - **Action**: When order status changes to `'shipped'` or `'delivered'`

21. **Item Delivered** ✅

    - **Feature**: Order status tracking
    - **Location**: `products/user_views.py` - `ship_order()` or
      `upload_shipment_proof()`
    - **Action**: When order status is `'delivered'`

22. **Order Canceled** ✅
    - **Feature**: Order status can be `'cancelled'`
    - **Action**: When order status changes to `'cancelled'`

### Offers

23. **Offer Accepted** ✅

    - **Feature**: `products/services.py` - `OfferService.accept_offer()`
    - **Location**: `products/offer_views.py` - `accept_offer()`
    - **Action**: When `offer.status = 'accepted'`

24. **Offer Declined** ✅

    - **Feature**: `products/services.py` - `OfferService.reject_offer()`
    - **Location**: `products/offer_views.py` - `reject_offer()`
    - **Action**: When `offer.status = 'rejected'`

25. **Counter‑Offer Received (Buyer)** ✅
    - **Feature**: `products/services.py` - `OfferService.counter_offer()`
    - **Location**: `products/offer_views.py` - `counter_offer()`
    - **Action**: When seller counters offer

### Returns & Disputes

26. **Dispute Resolved** ✅
    - **Feature**: `admin_dashboard/services.py` -
      `DisputeService.resolve_dispute()`
    - **Action**: When dispute status changes to `'resolved'`

### Payments

27. **Payment Failed** ✅
    - **Feature**: `payments/services.py` -
      `MoyasarPaymentService.process_payment()`
    - **Location**: `payments/views.py` - `process_payment()`
    - **Action**: When `payment.status = 'failed'`

### Reviews

28. **Review Your Purchase** ✅
    - **Feature**: Order tracking
    - **Location**: When order is `'delivered'` and `review_submitted = False`
    - **Action**: Could trigger after delivery, before review

---

## ✅ AFFILIATE Notifications - Feature Mapping

### Account & Setup

29. **Welcome to Affiliate Program** ✅

    - **Feature**: `authentication/services.py` -
      `AuthService.affiliate_signup()`
    - **Location**: `authentication/views.py` - `affiliate_signup()`
    - **Action**: When affiliate account is created

30. **Affiliate Payment Details Needed** ❓

    - **Status**: PARTIAL - Affiliates can add bank details during signup
    - **Question**: Should this trigger if affiliate signs up without bank
      details?
      Answer: Yes

31. **Payment Details Updated** ✅
    - **Feature**: Affiliate can update bank details
    - **Action**: When affiliate updates `bank_name`, `account_number`, etc.

### Earnings & Commissions

32. **Commission Earned** ✅

    - **Feature**: `products/services.py` -
      `OrderService.update_affiliate_earnings_on_payment_completion()`
    - **Action**: When affiliate commission is added to `pending_earnings`

33. **Commission Approved** ✅
    - **Feature**: `products/services.py` -
      `OrderService.update_affiliate_earnings_on_review_and_shipment()`
    - **Action**: When affiliate transaction status changes to `'paid'`

### Payouts

34. **Affiliate Payout Sent** ✅

    - **Feature**: `affiliates/services.py` -
      `AffiliateService.approve_payout()`
    - **Location**: `affiliates/views.py` - Admin approves payout
    - **Action**: When `payout.status = 'approved'`

35. **Affiliate Payout Failed** ✅
    - **Feature**: `affiliates/services.py` - `AffiliateService.reject_payout()`
    - **Location**: `affiliates/views.py` - Admin rejects payout
    - **Action**: When `payout.status = 'rejected'`

### Platform & Safety

36. **Affiliate Policy Violation** ❓

    - **Status**: NOT FOUND in codebase
    - **Question**: Is there a policy violation system for affiliates?
    Answer: when admin deactive any affiliate
37. **Affiliate Account Suspended** ✅

    - **Feature**: `authentication/models.py` - `Affiliate.status`
    - **Action**: When `affiliate.status = 'deactivated'`

38. **Affiliate Terms Updated** ❓
    - **Status**: NOT FOUND in codebase
    - **Question**: Is there a terms management system? Or should this be manual
      admin notification?
      Answer: skip this now

---

## ❓ Questions Before Implementation

### Missing Features to Clarify:

1. **Seller Verification**:

   - Does seller verification exist? If yes, where is it handled?
   - If no, should we skip this notification or create the feature?

  Answer:no and do not create that feature just add the notification when any buyer will create a listing and its role change from buyer to seller.
2. **Bank/Payment Setup for Sellers**:

   - Where do sellers add bank details?
   - Is this during signup or a separate profile update?
   - Should notification trigger if seller skips this during signup?
  Answer: make these fields in separate profile update and notification triger when users want to complete payment after checkout page he will recive that notification
3. **Shipping Label Ready**:

   - Is there a shipping label generation feature?
   - If no, should we remove this notification?
   Answer:no but there is a feature when payment success full status change to ready or anything else like that this notification will be trigered then

4. **Policy Violation Warning** (Seller & Affiliate):

   - Is there a policy violation tracking system?
   - How should violations be recorded and warnings sent?
   Answer:when admin suspend any seller buyer or affiliate

5. **Affiliate Payment Details Needed**:

   - Should this trigger if affiliate signs up without bank details?
   - Or only if they try to request payout without details?
   Answer:yes

6. **Affiliate Terms Updated**:
   - Is there a terms management system?
   - Or should this be a manual admin notification?
Answer:skip this for now
---

## 📋 Implementation Plan

Once you answer the questions above, I will:

1. **Create a notification helper service** that sends notifications to users
2. **Integrate notifications** into all the identified action points
3. **Handle missing features** based on your answers (skip, create, or mark as
   manual)
4. **Ensure notifications are sent** via WebSocket (already implemented) and
   optionally email

**Ready to proceed once you clarify the questions above!**
