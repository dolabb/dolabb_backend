# Payment Metadata & 401 Error Explanation

## Why Payment is Received in Moyasar Despite 401 Error

### Payment Flow:

1. **Frontend → Moyasar** (Payment Creation) ✅
   - Frontend calls Moyasar API directly to create payment
   - Payment is created successfully in Moyasar
   - Money is deducted and payment appears in Moyasar dashboard
   - **This works regardless of backend**

2. **Backend → Moyasar** (Payment Verification) ❌
   - After payment is created, backend tries to **verify** payment status
   - Backend calls Moyasar API to get payment details
   - **401 error happens here** - backend can't verify because key is wrong
   - **But payment already exists in Moyasar!**

### Key Point:
- **Payment creation** = Frontend → Moyasar (works fine)
- **Payment verification** = Backend → Moyasar (fails with 401)

The 401 error doesn't prevent payment creation - it only prevents backend verification. That's why you see the payment in Moyasar dashboard even though backend gets 401.

## Payment Metadata - Current vs Required

### Current Metadata in Moyasar:
```
type: cart
isGroup: false ✅ (correct)
product: - ❌ (missing product title)
orderId: 694098f52d1b5c8d31b69968 ✅
orderIds: 694098f52d1b5c8d31b69968 ✅
```

### Required Metadata:
```
type: cart
isGroup: false ✅ (already correct)
product: "Product Title Here" ✅ (needs to be added)
orderId: 694098f52d1b5c8d31b69968 ✅
orderIds: 694098f52d1b5c8d31b69968 ✅
```

## Where Metadata is Set

**Important**: Payment metadata is set by the **frontend** when creating the payment with Moyasar. The backend cannot change what's already in Moyasar.

### Frontend Should Send:
When creating payment with Moyasar, frontend should include metadata:

```typescript
const paymentData = {
  amount: amountInCents,
  currency: 'SAR',
  description: `Order ${orderNumber}`,
  metadata: {
    type: 'cart',
    isGroup: false,  // Ensure this is false for cart
    isGroupOrder: false,  // Also set this
    product: order.productTitle || product.title,  // Add product title
    orderId: orderId,
    orderIds: [orderId],  // Array with order IDs
    price: order.price,
    shipping: order.shipping,
    locale: 'en',
    // ... other metadata
  }
};
```

## Backend Enhancement (Already Implemented)

I've updated the backend to:
1. ✅ **Enhance payment record metadata** when processing webhook
   - Adds product title if missing
   - Ensures `isGroup: false` for cart type
   
2. ✅ **Find order using orderId** from request (fixed the "order not found" issue)

**Note**: This enhances the payment record in our database, but **doesn't change what's in Moyasar**. The metadata in Moyasar is set when payment is created by frontend.

## What Needs to be Fixed

### 1. Frontend: Add Product Title to Metadata

When creating payment with Moyasar, include product title:

```typescript
metadata: {
  type: 'cart',
  isGroup: false,
  product: productTitle,  // Add this
  orderId: orderId,
  // ... rest of metadata
}
```

### 2. Backend: Fix 401 Error (Still Needed)

The 401 error indicates the `MOYASAR_SECRET_KEY` in Render doesn't match your Moyasar dashboard.

**To Fix**:
1. Go to Moyasar Dashboard → Settings → API Keys
2. Copy the **exact** secret key
3. Verify it matches Render environment variable exactly
4. Check if payment belongs to same account as key

**Note**: Even with 401, payments will process (fallback active), but you should fix it for proper verification.

## Summary

✅ **Payment works** - Money is deducted and payment appears in Moyasar  
⚠️ **401 error** - Backend can't verify (but fallback processes payment)  
⚠️ **Missing product title** - Frontend needs to add it to metadata when creating payment  
✅ **isGroup is correct** - Already false, which is what you want  
✅ **Backend enhanced** - Will add product title to payment record metadata  

## Next Steps

1. **Frontend**: Add `product: productTitle` to metadata when creating payment
2. **Backend**: Fix `MOYASAR_SECRET_KEY` in Render to match Moyasar dashboard
3. **Test**: Verify metadata shows product title in Moyasar dashboard

