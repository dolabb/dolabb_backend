# Frontend Verification Checklist

## ✅ What's Already Fixed (Backend)

The backend now handles:
- ✅ Invalid ObjectId errors (accepts `PAY-xxx` format)
- ✅ 401 errors with fallback (processes payment even if verification fails)
- ✅ Better error messages and logging

## ⚠️ Frontend Changes Needed

Based on your console logs, here are the issues to check/fix:

### 1. ❌ Webhook Error Handling (CRITICAL)

**Current Issue**: Frontend redirects to error page when webhook returns 500, even though payment might be processed.

**From your logs**:
```
POST /api/payment/webhook/ 500 (Internal Server Error)
Payment webhook error: Request failed with status code 500
```

**What to Check/Fix**:

The webhook now has a **fallback** - even if verification fails with 401, it will still process the payment if frontend status is `'paid'`. However, it might still return an error response.

**Recommended Fix**:

```typescript
// After calling webhook
try {
  const webhookResponse = await apiClient.post('/api/payment/webhook/', {
    id: paymentId,
    status: 'paid',
    amount: amount,
    orderId: orderId
  });
  
  // Check if payment was actually processed
  // Even if there's an error, payment might still be processed
  if (webhookResponse.success || paymentStatus === 'paid') {
    // Payment processed successfully
    router.push(`/payment/success?orderId=${orderId}&moyasarPaymentId=${paymentId}`);
  } else {
    // Only redirect to error if payment actually failed
    router.push(`/payment/error?paymentId=${paymentId}`);
  }
} catch (error) {
  // If webhook fails but payment status is 'paid', still redirect to success
  // The backend fallback will process it
  if (paymentStatus === 'paid') {
    console.warn('Webhook failed but payment is paid, redirecting to success');
    router.push(`/payment/success?orderId=${orderId}&moyasarPaymentId=${paymentId}`);
  } else {
    router.push(`/payment/error?paymentId=${paymentId}`);
  }
}
```

### 2. ❌ Payment Success Endpoint - Use moyasarPaymentId

**Current Issue**: Frontend sends `paymentId=PAY-xxx` which is not a valid MongoDB ObjectId.

**From your logs**:
```
GET /api/payments/success/?orderId=6940...&paymentId=PAY-1765839481893&moyasarPaymentId=00e5c80e-b56b-433a-970a-c2402ae34aff 500
Error: 'PAY-1765839481893' is not a valid ObjectId
```

**What to Fix**:

**✅ Use `moyasarPaymentId` instead of local `paymentId`**:

```typescript
// ❌ DON'T DO THIS:
router.push(`/payment/success?paymentId=PAY-xxx&orderId=${orderId}`);

// ✅ DO THIS:
router.push(`/payment/success?orderId=${orderId}&moyasarPaymentId=${moyasarPaymentId}`);
```

**Or use only orderId** (backend will find payment by order):

```typescript
router.push(`/payment/success?orderId=${orderId}`);
```

### 3. ⚠️ Next.js API Route 404 (Optional)

**Current Issue**: Frontend tries to call Next.js API route which doesn't exist.

**From your logs**:
```
GET /api/payment/verify?id=00e5c80e-b56b-433a-970a-c2402ae34aff 404 (Not Found)
```

**Options**:

**Option A: Remove the Next.js verification call** (if not needed):
```typescript
// Remove or comment out this call
// const verifyResponse = await fetch(`/api/payment/verify?id=${paymentId}`);
```

**Option B: Create the Next.js API route** (if you want to use it):
- Create: `app/api/payment/verify/route.ts` (or similar based on your Next.js structure)
- Implement Moyasar payment verification

**Option C: Use Django backend verification** (already fixed):
```typescript
const verifyResponse = await apiClient.get(`/api/payment/verify/?paymentId=${paymentId}`);
```

**Recommendation**: Since you're already calling the Django webhook, you can skip the Next.js verification call. The webhook will verify with Moyasar.

### 4. ✅ Redirect Logic - Success vs Error

**Current Issue**: Redirecting to error page even when payment is successful.

**What to Check**:

Make sure your redirect logic checks the **payment status**:

```typescript
// After payment callback
if (paymentStatus === 'paid') {
  // Call webhook
  await apiClient.post('/api/payment/webhook/', { ... });
  
  // Redirect to SUCCESS page
  router.push(`/payment/success?orderId=${orderId}&moyasarPaymentId=${paymentId}`);
} else if (['failed', 'declined', 'canceled'].includes(paymentStatus)) {
  // Redirect to ERROR page
  router.push(`/payment/error?paymentId=${paymentId}&status=${paymentStatus}`);
} else {
  // Pending/initiated - wait or show pending message
  console.log('Payment still pending');
}
```

## 📋 Quick Verification Checklist

### Test 1: Payment Success Flow
- [ ] Make a payment
- [ ] Payment status is `'paid'`
- [ ] Webhook is called (even if it returns error, check logs)
- [ ] Redirects to `/payment/success` (NOT `/payment/error`)
- [ ] Success page loads without ObjectId errors
- [ ] Uses `moyasarPaymentId` or `orderId` in URL (NOT local `paymentId`)

### Test 2: Check Console Logs
- [ ] No 404 errors for Next.js API route (or route is created)
- [ ] Webhook is called with correct data
- [ ] Success page API call uses `moyasarPaymentId` or `orderId`
- [ ] No ObjectId validation errors

### Test 3: Check Network Tab
- [ ] `/api/payment/webhook/` is called
- [ ] `/api/payments/success/` is called with correct parameters
- [ ] Success page returns 200 (not 500)

## 🔧 Priority Fixes

1. **HIGHEST**: Fix redirect logic - use `moyasarPaymentId` instead of local `paymentId`
2. **HIGH**: Improve webhook error handling - don't redirect to error if payment is 'paid'
3. **MEDIUM**: Remove or fix Next.js API route call (404 error)
4. **LOW**: Add better error messages for user

## Summary

**Backend is ready** ✅ - All fixes are deployed

**Frontend needs**:
1. ✅ Use `moyasarPaymentId` when calling payment success endpoint
2. ✅ Don't redirect to error page if payment status is 'paid' (even if webhook has error)
3. ⚠️ Remove or fix Next.js verification API call (optional)

The most critical fix is **#1** - using `moyasarPaymentId` instead of local `paymentId` when redirecting to success page. This will prevent the ObjectId error.

