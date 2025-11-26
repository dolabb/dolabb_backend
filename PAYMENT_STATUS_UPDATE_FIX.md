# Payment Status Update Fix - Offer Status Not Updating to "Paid"

## Problem

The payment flow is working on the frontend, but the offer status is not updating to "paid" in the backend APIs. This is because:

1. **Frontend is using Next.js API routes** (`/api/payment/process/`, `/api/payment/webhook/`) instead of calling the Django backend directly
2. **Order is not created before payment** - Frontend generates a temporary `orderId` instead of calling the Django backend checkout API
3. **Webhook may not be calling Django backend** - The Next.js webhook route might not be forwarding to Django backend

---

## Root Cause Analysis

### Current Frontend Flow (from PAYMENT_FLOW_DOCUMENTATION.md):

```
1. Checkout Page → Collects address
2. Payment Page → Generates temporary orderId: "ORDER-1764174574974-8eqdp3m4l"
3. Calls Next.js API: POST /api/payment/process/ (NOT Django backend)
4. Calls Next.js API: POST /api/payment/webhook/ (NOT Django backend)
```

### Django Backend Expects:

```
1. POST /api/payment/checkout/ → Creates order with offer_id
2. POST /api/payment/process/ → Uses existing orderId from step 1
3. POST /api/payment/webhook/ → Updates order and offer status
```

**The mismatch:** Frontend is not calling Django backend checkout API to create the order first!

---

## Solution

### Option 1: Fix Frontend to Call Django Backend (Recommended)

Update the frontend payment flow to:

1. **Call Django Backend Checkout API First:**
   ```javascript
   // In checkout page, before redirecting to payment
   const checkoutResponse = await fetch('https://dolabb-backend-2vsj.onrender.com/api/payment/checkout/', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json',
     },
     body: JSON.stringify({
       offerId: offerId,  // IMPORTANT: Include offerId
       deliveryAddress: {
         fullName: fullName,
         phone: phone,
         address: address,
         city: city,
         postalCode: postalCode,
         country: country,
         additionalInfo: additionalInfo
       },
       affiliateCode: affiliateCode
     })
   });
   
   const checkoutData = await checkoutResponse.json();
   const realOrderId = checkoutData.orderId;  // Use this orderId for payment
   ```

2. **Use Real OrderId for Payment:**
   ```javascript
   // In payment page, use the real orderId from checkout
   POST /api/payment/process/
   {
     "orderId": realOrderId,  // From checkout API, not temporary
     "cardDetails": {...},
     "amount": 25500,
     "metadata": {
       "offerId": offerId  // Also include in metadata
     }
   }
   ```

3. **Call Django Backend Webhook:**
   ```javascript
   // After payment success, call Django backend webhook
   POST https://dolabb-backend-2vsj.onrender.com/api/payment/webhook/
   {
     "id": paymentId,
     "status": "paid",
     "amount": 25500,
     "offerId": offerId  // Include offerId
   }
   ```

---

### Option 2: Update Django Backend to Handle Missing Orders

If the frontend cannot be changed immediately, update the Django backend webhook to handle cases where order doesn't exist yet:

**Current Issue:** The webhook tries to find order by `payment_id`, but if order wasn't created, it fails.

**Fix:** The webhook already has logic to find order by `offerId` from metadata, but we need to ensure it's working correctly.

---

## Immediate Fix: Ensure Webhook Updates Offer Status

The Django backend webhook already has logic to update offer status directly if `offerId` is provided. Let's verify it's working:

### Check Webhook Logs

The webhook logs should show:
```
Extracted payment_id: xxx, status: paid, offerId: yyy
Directly updating offer yyy status from 'accepted' to 'paid'
✅ Directly updated offer yyy status to 'paid'
```

### Ensure Frontend Sends offerId in Webhook

Update the frontend webhook call to include `offerId`:

```javascript
// In payment callback or success handler
await fetch('https://dolabb-backend-2vsj.onrender.com/api/payment/webhook/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id: paymentId,
    status: 'paid',
    amount: amount,
    offerId: offerId  // CRITICAL: Must include this
  })
});
```

---

## Testing the Fix

### Test Flow:

1. **Create an offer** → Status: `pending`
2. **Seller accepts offer** → Status: `accepted`
3. **Buyer completes payment** → Should trigger webhook
4. **Check offer status** → Should be `paid`

### Verify in Database:

```python
# Check offer status
offer = Offer.objects(id=offer_id).first()
print(f"Offer status: {offer.status}")  # Should be 'paid'

# Check order payment status
order = Order.objects(offer_id=offer.id).first()
print(f"Order payment_status: {order.payment_status}")  # Should be 'completed'
```

### Check API Response:

```bash
GET /api/offers/accepted/
# Should show:
{
  "status": "paid",
  "paymentStatus": "completed"
}
```

---

## Debugging Steps

### 1. Check Webhook is Being Called

Add logging to see if webhook is receiving requests:

```python
# In payments/views.py payment_webhook
logger.info(f"Webhook called with data: {request.data}")
```

### 2. Check offerId is Being Passed

```python
# In payments/views.py payment_webhook
offer_id_from_request = data.get('offerId') or data.get('offer_id') or payment_data.get('offerId')
logger.info(f"Extracted offerId: {offer_id_from_request}")
```

### 3. Check Order Creation

```python
# Verify order was created with offer_id
order = Order.objects(offer_id=offer_id).first()
if order:
    logger.info(f"Order found: {order.id}, offer_id: {order.offer_id.id}")
else:
    logger.warning(f"No order found for offer_id: {offer_id}")
```

### 4. Check Payment Record

```python
# Verify payment record exists
payment = Payment.objects(moyasar_payment_id=payment_id).first()
if payment:
    logger.info(f"Payment found: {payment.id}, order_id: {payment.order_id.id}")
else:
    logger.warning(f"No payment found for moyasar_payment_id: {payment_id}")
```

---

## Recommended Frontend Changes

### Update Payment Flow:

```typescript
// 1. In checkout page - Call Django backend checkout API
async function handleCheckout(offerId: string) {
  const response = await fetch('https://dolabb-backend-2vsj.onrender.com/api/payment/checkout/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      offerId: offerId,
      deliveryAddress: {
        fullName: formData.fullName,
        phone: formData.phone,
        address: formData.address,
        city: formData.city,
        postalCode: formData.postalCode,
        country: formData.country,
      }
    })
  });
  
  const data = await response.json();
  if (data.success) {
    // Store real orderId
    sessionStorage.setItem('orderId', data.orderId);
    // Redirect to payment page
    router.push(`/payment?offerId=${offerId}&orderId=${data.orderId}`);
  }
}

// 2. In payment page - Use real orderId
async function handlePayment() {
  const orderId = sessionStorage.getItem('orderId'); // Real orderId from checkout
  const offerId = searchParams.get('offerId');
  
  // Call Django backend process_payment
  const response = await fetch('https://dolabb-backend-2vsj.onrender.com/api/payment/process/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      orderId: orderId,  // Real orderId
      cardDetails: cardDetails,
      amount: amount,
      metadata: {
        offerId: offerId  // Include in metadata
      }
    })
  });
  
  // Handle response...
}

// 3. After payment success - Call Django backend webhook
async function handlePaymentSuccess(paymentId: string, offerId: string) {
  await fetch('https://dolabb-backend-2vsj.onrender.com/api/payment/webhook/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      id: paymentId,
      status: 'paid',
      amount: amount,
      offerId: offerId  // CRITICAL: Include offerId
    })
  });
}
```

---

## Summary

**The issue:** Frontend is not creating orders through Django backend, so the webhook can't find the order to update the offer status.

**The fix:** 
1. Call Django backend `/api/payment/checkout/` first to create order with `offer_id`
2. Use the real `orderId` from checkout for payment
3. Ensure `offerId` is included in webhook call
4. Django backend webhook will automatically update offer status to "paid"

**Priority:** Update frontend to call Django backend checkout API before payment processing.

