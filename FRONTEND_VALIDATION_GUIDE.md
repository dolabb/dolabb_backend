# Frontend Validation Guide - Seller Cannot Buy Own Products

## Overview

The backend now prevents sellers from purchasing their own products. This
validation applies to:

1. Creating offers on own products
2. Purchasing via accepted offers
3. Direct purchases from cart/checkout

---

## Error Messages

The API will return these error messages when a seller tries to buy their own
product:

### 1. When Creating an Offer

```json
{
  "success": false,
  "error": "You cannot make an offer on your own product"
}
```

### 2. When Purchasing (Checkout/Order)

```json
{
  "success": false,
  "error": "You cannot purchase your own product"
}
```

**HTTP Status Code:** `400 Bad Request`

---

## Frontend Implementation

### 1. Offer Creation API

**Endpoint:** `POST /api/offers/create/`

#### React/TypeScript Example

```typescript
import { useState } from 'react';

interface CreateOfferResponse {
  success: boolean;
  offer?: {
    id: string;
    productId: string;
    buyerId: string;
    offerAmount: number;
    status: string;
    createdAt: string;
  };
  error?: string;
}

async function createOffer(
  token: string,
  productId: string,
  offerAmount: number,
  shippingAddress?: string,
  zipCode?: string,
  houseNumber?: string
): Promise<CreateOfferResponse> {
  try {
    const response = await fetch(
      'https://dolabb-backend-2vsj.onrender.com/api/offers/create/',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId,
          offerAmount,
          shippingAddress,
          zipCode,
          houseNumber,
        }),
      }
    );

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      success: false,
      error: 'Network error. Please try again.',
    };
  }
}

// React Component Example
function CreateOfferForm({
  productId,
  token,
}: {
  productId: string;
  token: string;
}) {
  const [offerAmount, setOfferAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    const result = await createOffer(token, productId, parseFloat(offerAmount));

    if (result.success) {
      setSuccess(true);
      // Handle success (e.g., show toast, redirect, etc.)
      console.log('Offer created:', result.offer);
    } else {
      // Handle error
      setError(result.error || 'Failed to create offer');

      // Specific handling for own product error
      if (result.error?.includes('your own product')) {
        // Show special message or disable offer button
        setError('You cannot make an offer on your own product');
      }
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className='error-message' role='alert'>
          {error}
        </div>
      )}
      {success && (
        <div className='success-message'>Offer submitted successfully!</div>
      )}
      <input
        type='number'
        value={offerAmount}
        onChange={e => setOfferAmount(e.target.value)}
        placeholder='Enter offer amount'
        required
        disabled={loading}
      />
      <button type='submit' disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Offer'}
      </button>
    </form>
  );
}
```

#### Vue.js Example

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <div v-if="error" class="error-message" role="alert">
      {{ error }}
    </div>
    <div v-if="success" class="success-message">
      Offer submitted successfully!
    </div>

    <input
      v-model="offerAmount"
      type="number"
      placeholder="Enter offer amount"
      required
      :disabled="loading"
    />

    <button type="submit" :disabled="loading">
      {{ loading ? 'Submitting...' : 'Submit Offer' }}
    </button>
  </form>
</template>

<script setup lang="ts">
  import { ref } from 'vue';

  const props = defineProps<{
    productId: string;
    token: string;
  }>();

  const offerAmount = ref('');
  const loading = ref(false);
  const error = ref<string | null>(null);
  const success = ref(false);

  async function handleSubmit() {
    loading.value = true;
    error.value = null;
    success.value = false;

    try {
      const response = await fetch(
        'https://dolabb-backend-2vsj.onrender.com/api/offers/create/',
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${props.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            productId: props.productId,
            offerAmount: parseFloat(offerAmount.value),
          }),
        }
      );

      const data = await response.json();

      if (data.success) {
        success.value = true;
        // Handle success
      } else {
        error.value = data.error || 'Failed to create offer';

        // Specific handling for own product error
        if (data.error?.includes('your own product')) {
          error.value = 'You cannot make an offer on your own product';
        }
      }
    } catch (err) {
      error.value = 'Network error. Please try again.';
    } finally {
      loading.value = false;
    }
  }
</script>
```

---

### 2. Checkout/Purchase API

**Endpoint:** `POST /api/payment/checkout/`

#### React/TypeScript Example

```typescript
interface CheckoutResponse {
  success: boolean;
  orderId?: string;
  checkoutData?: {
    product: string;
    price: number;
    offerPrice?: number;
    shipping: number;
    platformFee: number;
    total: number;
  };
  error?: string;
}

async function checkout(
  token: string,
  offerId: string | null,
  cartItems: string[],
  deliveryAddress: {
    fullName: string;
    phone: string;
    address: string;
    city: string;
    postalCode: string;
    country: string;
    additionalInfo?: string;
  },
  affiliateCode?: string
): Promise<CheckoutResponse> {
  try {
    const response = await fetch(
      'https://dolabb-backend-2vsj.onrender.com/api/payment/checkout/',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          offerId: offerId || undefined,
          cartItems,
          deliveryAddress,
          affiliateCode,
        }),
      }
    );

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      success: false,
      error: 'Network error. Please try again.',
    };
  }
}

// React Component Example
function CheckoutButton({
  offerId,
  productId,
  token,
}: {
  offerId: string | null;
  productId: string;
  token: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async () => {
    setLoading(true);
    setError(null);

    const result = await checkout(
      token,
      offerId,
      offerId ? [] : [productId], // If offerId exists, cartItems can be empty
      {
        fullName: 'John Doe',
        phone: '+1234567890',
        address: '123 Main St',
        city: 'City',
        postalCode: '12345',
        country: 'Country',
      }
    );

    if (result.success) {
      // Proceed to payment
      console.log('Order created:', result.orderId);
      // Redirect to payment page
    } else {
      setError(result.error || 'Checkout failed');

      // Specific handling for own product error
      if (result.error?.includes('your own product')) {
        setError('You cannot purchase your own product');
        // Optionally: Hide checkout button or show warning
      }
    }

    setLoading(false);
  };

  return (
    <div>
      {error && (
        <div className='error-message' role='alert'>
          {error}
        </div>
      )}
      <button onClick={handleCheckout} disabled={loading}>
        {loading ? 'Processing...' : 'Proceed to Checkout'}
      </button>
    </div>
  );
}
```

---

## UI/UX Recommendations

### 1. Pre-Validation (Before API Call)

Check if the user is the seller before showing offer/checkout buttons:

```typescript
// Check if current user is the product seller
function canUserPurchaseProduct(
  currentUserId: string,
  productSellerId: string
): boolean {
  return currentUserId !== productSellerId;
}

// In your component
function ProductPage({ product, currentUser }) {
  const canPurchase = canUserPurchaseProduct(currentUser.id, product.sellerId);

  return (
    <div>
      {canPurchase ? (
        <button onClick={handleOffer}>Make Offer</button>
      ) : (
        <div className='info-message'>
          This is your own product. You cannot make offers or purchase it.
        </div>
      )}
    </div>
  );
}
```

### 2. Error Display Best Practices

```typescript
// Error message component with different styles based on error type
function ErrorMessage({ error }: { error: string }) {
  const isOwnProductError = error?.includes('your own product');

  return (
    <div
      className={`error-container ${isOwnProductError ? 'warning' : 'error'}`}
      role='alert'
    >
      <Icon name={isOwnProductError ? 'warning' : 'error'} />
      <span>{error}</span>
    </div>
  );
}
```

### 3. Toast/Notification Integration

```typescript
import { toast } from 'react-toastify';

async function createOffer(...) {
  const result = await createOffer(...);

  if (result.success) {
    toast.success('Offer submitted successfully!');
  } else {
    if (result.error?.includes('your own product')) {
      toast.warning('You cannot make an offer on your own product');
    } else {
      toast.error(result.error || 'Failed to create offer');
    }
  }
}
```

---

## Complete Error Handling Utility

```typescript
// utils/offerErrors.ts

export enum OfferErrorType {
  OWN_PRODUCT = 'OWN_PRODUCT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

export interface ParsedError {
  type: OfferErrorType;
  message: string;
  originalError: string;
}

export function parseOfferError(error: string | undefined): ParsedError {
  if (!error) {
    return {
      type: OfferErrorType.UNKNOWN_ERROR,
      message: 'An unexpected error occurred',
      originalError: '',
    };
  }

  // Check for own product error
  if (error.toLowerCase().includes('your own product')) {
    return {
      type: OfferErrorType.OWN_PRODUCT,
      message: 'You cannot make an offer or purchase your own product',
      originalError: error,
    };
  }

  // Check for network errors
  if (
    error.toLowerCase().includes('network') ||
    error.toLowerCase().includes('fetch')
  ) {
    return {
      type: OfferErrorType.NETWORK_ERROR,
      message: 'Network error. Please check your connection and try again.',
      originalError: error,
    };
  }

  // Validation errors
  if (
    error.toLowerCase().includes('cannot be greater') ||
    error.toLowerCase().includes('not found') ||
    error.toLowerCase().includes('required')
  ) {
    return {
      type: OfferErrorType.VALIDATION_ERROR,
      message: error,
      originalError: error,
    };
  }

  // Unknown error
  return {
    type: OfferErrorType.UNKNOWN_ERROR,
    message: error,
    originalError: error,
  };
}

// Usage
function handleOfferError(error: string) {
  const parsed = parseOfferError(error);

  switch (parsed.type) {
    case OfferErrorType.OWN_PRODUCT:
      // Hide offer button, show info message
      showInfoMessage(parsed.message);
      break;
    case OfferErrorType.NETWORK_ERROR:
      showRetryButton();
      break;
    case OfferErrorType.VALIDATION_ERROR:
      showValidationError(parsed.message);
      break;
    default:
      showGenericError(parsed.message);
  }
}
```

---

## React Hook Example

```typescript
// hooks/useOffer.ts
import { useState } from 'react';
import { parseOfferError, OfferErrorType } from '../utils/offerErrors';

export function useOffer() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ParsedError | null>(null);

  const createOffer = async (
    token: string,
    productId: string,
    offerAmount: number
  ) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        'https://dolabb-backend-2vsj.onrender.com/api/offers/create/',
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            productId,
            offerAmount,
          }),
        }
      );

      const data = await response.json();

      if (!data.success) {
        const parsed = parseOfferError(data.error);
        setError(parsed);
        return { success: false, error: parsed };
      }

      return { success: true, offer: data.offer };
    } catch (err) {
      const parsed = parseOfferError('Network error');
      setError(parsed);
      return { success: false, error: parsed };
    } finally {
      setLoading(false);
    }
  };

  return {
    createOffer,
    loading,
    error,
    isOwnProductError: error?.type === OfferErrorType.OWN_PRODUCT,
  };
}

// Usage in component
function OfferForm({ productId, token }) {
  const { createOffer, loading, error, isOwnProductError } = useOffer();

  const handleSubmit = async (offerAmount: number) => {
    const result = await createOffer(token, productId, offerAmount);

    if (result.success) {
      // Handle success
    }
  };

  return (
    <div>
      {isOwnProductError && (
        <div className='warning-banner'>
          You cannot make an offer on your own product
        </div>
      )}
      {/* Rest of form */}
    </div>
  );
}
```

---

## Testing Checklist

### 1. Test Offer Creation

- [ ] Seller tries to create offer on own product → Should show error
- [ ] Buyer creates offer on seller's product → Should succeed
- [ ] Error message displays correctly
- [ ] UI updates appropriately (button disabled, message shown)

### 2. Test Checkout

- [ ] Seller tries to checkout own product → Should show error
- [ ] Buyer checks out seller's product → Should succeed
- [ ] Error message displays correctly
- [ ] Checkout button disabled/hidden when appropriate

### 3. Test Edge Cases

- [ ] Network error handling
- [ ] Multiple rapid clicks (prevent duplicate requests)
- [ ] Loading states
- [ ] Error recovery (retry button)

---

## Example: Complete Product Page Component

```typescript
import React, { useState, useEffect } from 'react';
import { useOffer } from '../hooks/useOffer';
import { canUserPurchaseProduct } from '../utils/productUtils';

interface Product {
  id: string;
  sellerId: string;
  title: string;
  price: number;
}

function ProductPage({
  product,
  currentUser,
}: {
  product: Product;
  currentUser: any;
}) {
  const [showOfferForm, setShowOfferForm] = useState(false);
  const [offerAmount, setOfferAmount] = useState('');
  const { createOffer, loading, error, isOwnProductError } = useOffer();

  const canPurchase = canUserPurchaseProduct(currentUser.id, product.sellerId);

  const handleOfferSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!canPurchase) {
      return; // Should not reach here if UI is correct
    }

    const result = await createOffer(
      currentUser.token,
      product.id,
      parseFloat(offerAmount)
    );

    if (result.success) {
      setShowOfferForm(false);
      // Show success message
    }
  };

  return (
    <div className='product-page'>
      <h1>{product.title}</h1>
      <p>Price: ${product.price}</p>

      {canPurchase ? (
        <>
          {!showOfferForm ? (
            <button onClick={() => setShowOfferForm(true)}>
              Make an Offer
            </button>
          ) : (
            <form onSubmit={handleOfferSubmit}>
              {error && (
                <div className={`error ${isOwnProductError ? 'warning' : ''}`}>
                  {error.message}
                </div>
              )}
              <input
                type='number'
                value={offerAmount}
                onChange={e => setOfferAmount(e.target.value)}
                placeholder='Enter offer amount'
                required
                disabled={loading}
              />
              <button type='submit' disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Offer'}
              </button>
              <button type='button' onClick={() => setShowOfferForm(false)}>
                Cancel
              </button>
            </form>
          )}
        </>
      ) : (
        <div className='info-banner'>
          <p>
            This is your own product. You cannot make offers or purchase it.
          </p>
        </div>
      )}
    </div>
  );
}
```

---

## Summary

1. **Always check API response** - Look for `success: false` and `error` field
2. **Handle specific error messages** - Check for "your own product" in error
   text
3. **Pre-validate when possible** - Check user ID vs seller ID before showing
   buttons
4. **Show appropriate UI** - Disable buttons, show warnings, or hide options for
   own products
5. **Provide clear feedback** - Use toast notifications, error messages, or info
   banners
6. **Test thoroughly** - Test both success and error scenarios

---

## Support

For questions or issues with frontend integration, contact the development team.

**API Base URL:** `https://dolabb-backend-2vsj.onrender.com`
