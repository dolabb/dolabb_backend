# Frontend Upgrade Guide: Shipment Proof Security Update

This guide outlines the frontend changes required after the backend security
update that requires shipment proof before earnings become available for payout.

---

## Table of Contents

1. [Overview of Changes](#overview-of-changes)
2. [Breaking Changes](#breaking-changes)
3. [Required Frontend Updates](#required-frontend-updates)
4. [API Response Changes](#api-response-changes)
5. [Component Updates](#component-updates)
6. [Migration Steps](#migration-steps)
7. [Testing Checklist](#testing-checklist)

---

## Overview of Changes

### What Changed?

The backend now enforces a **shipment proof requirement** before seller earnings
become available for payout:

- **Before:** Earnings were available immediately after payment completion
- **After:** Earnings are locked until shipment proof is uploaded

### Key Changes:

1. **Earnings API Response** - Now includes `pendingShipmentProof` field
2. **Ship Order Endpoint** - Now accepts shipment proof upload
3. **Available Balance** - Only includes orders with shipment proof
4. **Pending Payouts** - Now includes orders waiting for shipment proof

---

## Breaking Changes

### ⚠️ Important Breaking Changes:

1. **Earnings Response Structure Changed**

   - New field: `pendingShipmentProof`
   - `availableBalance` calculation changed (now excludes orders without
     shipment proof)

2. **Ship Order Endpoint Enhanced**

   - Now accepts `shipmentProof` file or `shipmentProofUrl`
   - Response includes shipment proof information

3. **Earnings Logic Changed**
   - `totalEarnings` only includes orders with shipment proof
   - `pendingPayouts` includes both payout requests AND orders without shipment
     proof

---

## Required Frontend Updates

### 1. Update TypeScript/JavaScript Types

**File:** `types/seller.ts` or `types/api.ts`

**Before:**

```typescript
export interface SellerEarnings {
  totalEarnings: number;
  totalPayouts: number;
  pendingPayouts: number;
  availableBalance: number;
}
```

**After:**

```typescript
export interface SellerEarnings {
  totalEarnings: number;
  totalPayouts: number;
  pendingPayouts: number;
  availableBalance: number;
  pendingShipmentProof: number; // NEW: Amount locked until shipment proof uploaded
}
```

---

### 2. Update Earnings Display Component

**File:** `components/dashboard/PayoutTab.tsx` or similar

**Add Pending Shipment Proof Display:**

```tsx
// Add this card to your earnings summary
<div className='earnings-card warning'>
  <h3>Pending Shipment Proof</h3>
  <p className='amount'>{earnings.pendingShipmentProof} SAR</p>
  <small>Upload shipment proof to unlock these earnings</small>
</div>
```

**Full Updated Earnings Cards:**

```tsx
<div className='earnings-grid'>
  <div className='earnings-card'>
    <h3>Total Earnings</h3>
    <p className='amount'>{earnings.totalEarnings} SAR</p>
    <small>From orders with shipment proof</small>
  </div>

  <div className='earnings-card'>
    <h3>Total Payouts</h3>
    <p className='amount'>{earnings.totalPayouts} SAR</p>
    <small>Approved payout requests</small>
  </div>

  <div className='earnings-card warning'>
    <h3>Pending Payouts</h3>
    <p className='amount'>{earnings.pendingPayouts} SAR</p>
    <small>Payout requests + orders without shipment proof</small>
  </div>

  <div className='earnings-card highlight'>
    <h3>Available Balance</h3>
    <p className='amount'>{earnings.availableBalance} SAR</p>
    <small>Ready for withdrawal</small>
  </div>

  {/* NEW: Pending Shipment Proof Card */}
  {earnings.pendingShipmentProof > 0 && (
    <div className='earnings-card warning'>
      <h3>Pending Shipment Proof</h3>
      <p className='amount'>{earnings.pendingShipmentProof} SAR</p>
      <small>Upload shipment proof to unlock</small>
    </div>
  )}
</div>
```

---

### 3. Update Ship Order Component

**File:** `components/orders/ShipOrderModal.tsx` or similar

**Before:**

```tsx
const handleShipOrder = async () => {
  await api.put(`/api/user/payments/${orderId}/ship/`, {
    trackingNumber: trackingNumber,
  });
};
```

**After:**

```tsx
const handleShipOrder = async (formData: FormData) => {
  // Include shipment proof in the request
  await api.put(`/api/user/payments/${orderId}/ship/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Or with file input
const handleShipOrder = async () => {
  const formData = new FormData();
  formData.append('trackingNumber', trackingNumber);

  if (shipmentProofFile) {
    formData.append('shipmentProof', shipmentProofFile);
  } else if (shipmentProofUrl) {
    formData.append('shipmentProofUrl', shipmentProofUrl);
  }

  await api.put(`/api/user/payments/${orderId}/ship/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
```

**Complete Ship Order Component Example:**

```tsx
import React, { useState } from 'react';
import { useShipOrderMutation } from '../api/ordersApi';

const ShipOrderModal = ({ orderId, onClose }) => {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [shipmentProofFile, setShipmentProofFile] = useState<File | null>(null);
  const [shipmentProofUrl, setShipmentProofUrl] = useState('');
  const [uploadMethod, setUploadMethod] = useState<'file' | 'url'>('file');

  const shipOrderMutation = useShipOrderMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!trackingNumber.trim()) {
      alert('Tracking number is required');
      return;
    }

    // IMPORTANT: Shipment proof is now required for earnings
    if (!shipmentProofFile && !shipmentProofUrl.trim()) {
      alert(
        'Shipment proof is required. Upload proof to unlock earnings for this order.'
      );
      return;
    }

    const formData = new FormData();
    formData.append('trackingNumber', trackingNumber);

    if (uploadMethod === 'file' && shipmentProofFile) {
      formData.append('shipmentProof', shipmentProofFile);
    } else if (uploadMethod === 'url' && shipmentProofUrl) {
      formData.append('shipmentProofUrl', shipmentProofUrl);
    }

    try {
      await shipOrderMutation.mutateAsync({
        orderId,
        formData,
      });

      alert(
        'Order shipped successfully! Earnings for this order are now available for payout.'
      );
      onClose();
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to ship order');
    }
  };

  return (
    <div className='modal'>
      <h2>Ship Order</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Tracking Number *</label>
          <input
            type='text'
            value={trackingNumber}
            onChange={e => setTrackingNumber(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Upload Method</label>
          <select
            value={uploadMethod}
            onChange={e => setUploadMethod(e.target.value as 'file' | 'url')}
          >
            <option value='file'>Upload File</option>
            <option value='url'>Provide URL</option>
          </select>
        </div>

        {uploadMethod === 'file' ? (
          <div>
            <label>Shipment Proof Image *</label>
            <input
              type='file'
              accept='image/*'
              onChange={e => setShipmentProofFile(e.target.files?.[0] || null)}
              required
            />
            <small>
              Upload proof of shipment (receipt, tracking label, etc.)
            </small>
          </div>
        ) : (
          <div>
            <label>Shipment Proof URL *</label>
            <input
              type='url'
              value={shipmentProofUrl}
              onChange={e => setShipmentProofUrl(e.target.value)}
              placeholder='https://example.com/shipment-proof.jpg'
              required
            />
            <small>Provide direct URL to shipment proof image</small>
          </div>
        )}

        <div className='warning-box'>
          <strong>⚠️ Important:</strong> Shipment proof is required for earnings
          to become available for payout.
        </div>

        <div className='button-group'>
          <button type='button' onClick={onClose}>
            Cancel
          </button>
          <button type='submit' disabled={shipOrderMutation.isLoading}>
            {shipOrderMutation.isLoading ? 'Shipping...' : 'Ship Order'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ShipOrderModal;
```

---

### 4. Update Sale History Component

**File:** `components/dashboard/SaleHistoryTab.tsx`

**Add Shipment Proof Status Indicator:**

```tsx
{
  payments?.map(payment => (
    <div key={payment.id} className='payment-card'>
      {/* Existing payment details */}

      {/* NEW: Shipment Proof Status */}
      {payment.paymentStatus === 'completed' && (
        <div className='shipment-proof-status'>
          {payment.shipmentProof ? (
            <span className='status-badge success'>
              ✓ Shipment Proof Uploaded
            </span>
          ) : (
            <span className='status-badge warning'>
              ⚠ Pending Shipment Proof
            </span>
          )}
        </div>
      )}

      {/* Show warning if payment completed but no shipment proof */}
      {payment.paymentStatus === 'completed' && !payment.shipmentProof && (
        <div className='warning-message'>
          <strong>Action Required:</strong> Upload shipment proof to unlock
          earnings for this order.
          <button onClick={() => openShipModal(payment.id)}>
            Upload Shipment Proof
          </button>
        </div>
      )}
    </div>
  ));
}
```

---

### 5. Update API Client Functions

**File:** `api/ordersApi.ts` or `api/sellerApi.ts`

**Update Ship Order Function:**

```typescript
// Before
export const shipOrder = async (orderId: string, trackingNumber: string) => {
  const response = await api.put(`/api/user/payments/${orderId}/ship/`, {
    trackingNumber,
  });
  return response.data;
};

// After
export const shipOrder = async (
  orderId: string,
  data: {
    trackingNumber: string;
    shipmentProof?: File;
    shipmentProofUrl?: string;
  }
) => {
  const formData = new FormData();
  formData.append('trackingNumber', data.trackingNumber);

  if (data.shipmentProof) {
    formData.append('shipmentProof', data.shipmentProof);
  } else if (data.shipmentProofUrl) {
    formData.append('shipmentProofUrl', data.shipmentProofUrl);
  }

  const response = await api.put(
    `/api/user/payments/${orderId}/ship/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};
```

**Update Earnings Query:**

```typescript
// The response now includes pendingShipmentProof
export const getSellerEarnings = async () => {
  const response = await api.get('/api/seller/earnings/');
  return response.data; // Now includes pendingShipmentProof
};
```

---

### 6. Add Shipment Proof Upload to Sale History

**Add Upload Button in Sale History:**

```tsx
// In SaleHistoryTab component
const handleUploadShipmentProof = async (orderId: string) => {
  // Open modal or navigate to upload page
  setSelectedOrderId(orderId);
  setShowShipModal(true);
};

// In payment card
{
  payment.paymentStatus === 'completed' && !payment.shipmentProof && (
    <button
      className='btn-primary'
      onClick={() => handleUploadShipmentProof(payment.id)}
    >
      Upload Shipment Proof
    </button>
  );
}
```

---

### 7. Update UI/UX Messages

**Add Informative Messages:**

```tsx
// In PayoutTab component
{
  earnings.pendingShipmentProof > 0 && (
    <div className='info-banner warning'>
      <h4>⚠️ Action Required</h4>
      <p>
        You have {earnings.pendingShipmentProof} SAR locked until you upload
        shipment proof for completed orders.
      </p>
      <button onClick={() => navigateToSaleHistory()}>
        View Orders & Upload Proof
      </button>
    </div>
  );
}
```

---

## API Response Changes

### Earnings API Response

**Before:**

```json
{
  "success": true,
  "earnings": {
    "totalEarnings": 5000.0,
    "totalPayouts": 3000.0,
    "pendingPayouts": 500.0,
    "availableBalance": 1500.0
  }
}
```

**After:**

```json
{
  "success": true,
  "earnings": {
    "totalEarnings": 5000.0,
    "totalPayouts": 3000.0,
    "pendingPayouts": 500.0,
    "availableBalance": 1500.0,
    "pendingShipmentProof": 200.0 // NEW FIELD
  }
}
```

### Ship Order Response

**Before:**

```json
{
  "success": true,
  "payment": {
    "id": "order_id",
    "status": "shipped",
    "trackingNumber": "TRACK123"
  }
}
```

**After:**

```json
{
  "success": true,
  "message": "Order shipped with shipment proof. Earnings will be available for payout.",
  "payment": {
    "id": "order_id",
    "status": "shipped",
    "trackingNumber": "TRACK123",
    "shipmentProof": "https://example.com/shipment-proof.jpg" // NEW FIELD
  }
}
```

---

## Component Updates

### 1. PayoutTab Component

**Required Changes:**

- ✅ Display `pendingShipmentProof` field
- ✅ Show warning when `pendingShipmentProof > 0`
- ✅ Update available balance calculation logic
- ✅ Add link to sale history for uploading proof

### 2. SaleHistoryTab Component

**Required Changes:**

- ✅ Show shipment proof status for each order
- ✅ Add "Upload Shipment Proof" button for orders without proof
- ✅ Highlight orders requiring action
- ✅ Show warning message for locked earnings

### 3. ShipOrderModal Component

**Required Changes:**

- ✅ Add shipment proof file upload field
- ✅ Add shipment proof URL input option
- ✅ Make shipment proof required
- ✅ Show warning about earnings requirement
- ✅ Update API call to include shipment proof

### 4. OrderCard/PaymentCard Component

**Required Changes:**

- ✅ Display shipment proof status badge
- ✅ Show "Upload Proof" button when needed
- ✅ Visual indicator for locked earnings

---

## Migration Steps

### Step 1: Update Types

1. Add `pendingShipmentProof` to `SellerEarnings` interface
2. Update any TypeScript types related to earnings

### Step 2: Update API Functions

1. Update `shipOrder` function to accept shipment proof
2. Update `getSellerEarnings` to handle new response
3. Test API calls with new structure

### Step 3: Update Components

1. **PayoutTab:**

   - Add pending shipment proof display
   - Update earnings cards
   - Add warning messages

2. **SaleHistoryTab:**

   - Add shipment proof status indicators
   - Add upload buttons
   - Add warning messages

3. **ShipOrderModal:**
   - Add shipment proof upload fields
   - Make proof required
   - Update form submission

### Step 4: Update Styling

1. Add styles for warning cards
2. Add styles for status badges
3. Add styles for info banners

### Step 5: Testing

1. Test earnings display with new field
2. Test shipment proof upload
3. Test earnings unlock after proof upload
4. Test payout request with new balance calculation

---

## Testing Checklist

### ✅ Earnings Display

- [ ] `pendingShipmentProof` field displays correctly
- [ ] Warning shows when `pendingShipmentProof > 0`
- [ ] Available balance excludes locked earnings
- [ ] Total earnings only shows orders with proof

### ✅ Ship Order Flow

- [ ] Shipment proof upload works (file)
- [ ] Shipment proof URL works
- [ ] Validation prevents shipping without proof
- [ ] Success message shows after upload
- [ ] Earnings update after proof upload

### ✅ Sale History

- [ ] Shipment proof status displays correctly
- [ ] Upload button shows for orders without proof
- [ ] Warning messages display correctly
- [ ] Navigation to upload works

### ✅ Payout Request

- [ ] Only available balance can be requested
- [ ] Locked earnings cannot be requested
- [ ] Validation prevents over-requesting
- [ ] Error messages are clear

### ✅ Edge Cases

- [ ] Orders with payment but no proof show as locked
- [ ] Orders with proof show as available
- [ ] Zero pending proof displays correctly
- [ ] Large numbers format correctly

---

## UI/UX Recommendations

### 1. Visual Indicators

**Use color coding:**

- 🟢 Green: Shipment proof uploaded, earnings available
- 🟡 Yellow: Payment completed, proof pending
- 🔴 Red: Action required

### 2. Clear Messaging

**Good Messages:**

- "Upload shipment proof to unlock 200 SAR"
- "Earnings available after shipment proof upload"
- "This order's earnings are locked until proof is uploaded"

**Bad Messages:**

- "Proof needed" (too vague)
- "Error" (not helpful)

### 3. User Guidance

**Add tooltips:**

- "Shipment proof is required to unlock earnings for payout"
- "Upload a photo of your shipping receipt or tracking label"
- "Earnings become available immediately after proof upload"

### 4. Progress Indicators

**Show progress:**

- "3 orders pending shipment proof"
- "200 SAR waiting for proof upload"
- Progress bar showing locked vs available

---

## Code Examples

### Complete PayoutTab Update

```tsx
import React from 'react';
import { useSellerEarnings } from '../hooks/useSellerApi';

const PayoutTab = () => {
  const { data: earningsData, isLoading } = useSellerEarnings();
  const earnings = earningsData?.earnings || {};

  return (
    <div className='payout-tab'>
      <h2>Payout Management</h2>

      {/* Earnings Summary */}
      <div className='earnings-grid'>
        <div className='earnings-card'>
          <h3>Total Earnings</h3>
          <p className='amount'>{earnings.totalEarnings} SAR</p>
          <small>From orders with shipment proof</small>
        </div>

        <div className='earnings-card'>
          <h3>Total Payouts</h3>
          <p className='amount'>{earnings.totalPayouts} SAR</p>
        </div>

        <div className='earnings-card warning'>
          <h3>Pending Payouts</h3>
          <p className='amount'>{earnings.pendingPayouts} SAR</p>
        </div>

        <div className='earnings-card highlight'>
          <h3>Available Balance</h3>
          <p className='amount'>{earnings.availableBalance} SAR</p>
          <small>Ready for withdrawal</small>
        </div>

        {/* NEW: Pending Shipment Proof */}
        {earnings.pendingShipmentProof > 0 && (
          <div className='earnings-card warning'>
            <h3>Pending Shipment Proof</h3>
            <p className='amount'>{earnings.pendingShipmentProof} SAR</p>
            <small>Upload proof to unlock</small>
          </div>
        )}
      </div>

      {/* Warning Banner */}
      {earnings.pendingShipmentProof > 0 && (
        <div className='info-banner warning'>
          <h4>⚠️ Action Required</h4>
          <p>
            You have {earnings.pendingShipmentProof} SAR locked until you upload
            shipment proof. Upload proof to make these earnings available for
            payout.
          </p>
          <button onClick={() => navigateToSaleHistory()}>
            View Orders & Upload Proof
          </button>
        </div>
      )}

      {/* Rest of payout form... */}
    </div>
  );
};
```

---

## Common Issues & Solutions

### Issue 1: Earnings Not Updating After Proof Upload

**Solution:** Ensure you're refetching earnings data after successful upload:

```tsx
const shipOrderMutation = useMutation(shipOrder, {
  onSuccess: () => {
    queryClient.invalidateQueries(['sellerEarnings']);
    queryClient.invalidateQueries(['saleHistory']);
  },
});
```

### Issue 2: File Upload Not Working

**Solution:** Ensure FormData is used correctly:

```tsx
const formData = new FormData();
formData.append('shipmentProof', file);
// Don't set Content-Type header manually, browser will set it
```

### Issue 3: TypeScript Errors

**Solution:** Update all type definitions:

```typescript
// Add to your types file
export interface SellerEarnings {
  totalEarnings: number;
  totalPayouts: number;
  pendingPayouts: number;
  availableBalance: number;
  pendingShipmentProof: number; // Add this
}
```

---

## Support

If you encounter issues during the upgrade:

1. Check the API documentation: `SELLER_SALE_HISTORY_PAYOUT_GUIDE.md`
2. Review the integration guide: `SELLER_INTEGRATION_GUIDE.md`
3. Test API endpoints directly using Postman/curl
4. Check browser console for errors
5. Verify backend is running latest version

---

## Summary

### Critical Updates Required:

1. ✅ Add `pendingShipmentProof` field to earnings display
2. ✅ Update ship order to require shipment proof
3. ✅ Add shipment proof upload UI
4. ✅ Update earnings calculation logic
5. ✅ Add warning messages for locked earnings
6. ✅ Update TypeScript types

### Timeline Recommendation:

- **Phase 1 (Critical):** Update earnings display and ship order (1-2 days)
- **Phase 2 (Important):** Add upload UI and warnings (2-3 days)
- **Phase 3 (Enhancement):** Improve UX and messaging (1-2 days)

**Total Estimated Time:** 4-7 days

---

**Last Updated:** 2024-01-15 **Backend Version:** v1.1.0 (with shipment proof
security)
