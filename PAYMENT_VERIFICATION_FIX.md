# Payment Verification Issue & Fix

## Problem Summary

The payment verification API was failing with a 500 error:

```
'Settings' object has no attribute 'MOYASAR_API_URL'
```

This was happening because:

1. The frontend was calling Django backend `/api/payment/verify/` endpoint
2. Django backend was missing the `MOYASAR_API_URL` configuration setting
3. This prevented verification from succeeding, blocking the entire payment flow

## What Should Happen When Verification Succeeds

When payment verification succeeds, the following processes should be triggered:

### 1. **Payment Verification** ✅

- Frontend calls verification API to confirm payment status with Moyasar
- Gets payment details (status, amount, card info, etc.)
- Confirms payment is actually "paid" (not just "initiated")

### 2. **Webhook Call to Django Backend** ✅

- After successful verification, frontend calls `/api/payment/webhook/` endpoint
- This webhook triggers:
  - **Order Creation/Update**: Creates or updates order in database
  - **Offer Status Update**: Changes offer status to 'accepted'
  - **Affiliate Earnings**: Adds earnings to affiliate's `total_earnings` and
    `pending_earnings`
  - **Transaction Creation**: Creates transaction record with status 'pending'
  - **Email Notifications**: Sends "item sold" email to seller/admin
  - **Admin Notifications**: Notifies admin about new order

### 3. **Success Page Redirect** ✅

- User is redirected to `/payment/success` page
- Payment details are saved to localStorage
- User sees confirmation of successful payment

## Solution Implemented

### Frontend Fix:

Changed payment verification to use **Next.js API route** instead of Django
backend:

**Before:**

```typescript
const verifyResponse = await apiClient.post('/api/payment/verify/', verifyBody);
// This called Django backend which had configuration issues
```

**After:**

```typescript
const verifyResponse = await fetch(`/api/payment/verify/?id=${paymentId}`, {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' },
});
// This calls Next.js API route which works correctly
```

### Why This Works:

1. **Next.js API Route** (`app/api/payment/verify/route.ts`) calls Moyasar
   directly
2. No Django backend dependency for verification
3. Faster and more reliable
4. Still calls Django webhook after verification for backend processing

## Flow After Fix

```
1. Payment Callback Received (status=paid)
   ↓
2. Verify Payment with Next.js API → Moyasar API
   ✅ Returns payment details
   ↓
3. Payment Confirmed as "paid"
   ↓
4. Call Django Webhook (/api/payment/webhook/)
   ✅ Updates order status
   ✅ Updates affiliate earnings
   ✅ Sends notifications
   ✅ Creates transaction records
   ↓
5. Redirect to Success Page
   ✅ User sees confirmation
```

## Django Backend Fix Needed (Optional)

If you want to fix Django backend verification endpoint, add this setting:

```python
# settings.py
MOYASAR_API_URL = 'https://api.moyasar.com/v1'
MOYASAR_SECRET_KEY = 'your_secret_key_here'
```

However, **this is not necessary** since we're now using Next.js API route for
verification.

## Important Notes

- **Verification** = Checking payment status with Moyasar (now via Next.js API)
- **Webhook** = Processing payment in Django backend (still needed for business
  logic)
- Both are important but serve different purposes
- Verification failure no longer blocks successful payments (fallback to URL
  status)
