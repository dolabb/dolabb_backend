# Payment System Flow Documentation

## Overview
This document explains the complete payment flow from the checkout page through all API endpoints to payment completion, including 3D Secure (3DS) authentication handling.

---

## Flow Diagram

```
Checkout Page → Payment Page → Payment Process API → Moyasar API
                                                          ↓
Payment Callback ← Moyasar 3DS ← Transaction URL (if 3DS required)
     ↓
Verify API → Webhook API → Success Page
```

---

## Step-by-Step Flow

### 1. **Checkout Page** (`/checkout`)
**File:** `app/[locale]/(dashboard)/checkout/page.tsx`

**Purpose:** Collects shipping address information from the buyer.

**Process:**
- User enters delivery address (name, phone, address, city, postal code, country)
- Form validation ensures all required fields are filled
- On submit, redirects to payment page with offer data in URL parameters:
  - `offerId`
  - `product`
  - `size`
  - `price`
  - `offerPrice`
  - `shipping`

**No API calls at this stage** - just data collection and navigation.

---

### 2. **Payment Page** (`/payment`)
**File:** `app/[locale]/(dashboard)/payment/page.tsx`

**Purpose:** Collects payment card details and processes payment.

**Process:**

#### 2.1 User Input
- User enters card details:
  - Cardholder name (must be at least 2 words)
  - Card number (formatted with spaces)
  - Expiry month and year
  - CVC

#### 2.2 Payment Submission (`handleSubmit`)
When user clicks "Complete Payment":

1. **Generate Order ID:**
   ```javascript
   const orderId = `ORDER-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
   ```

2. **Call Payment Process API:**
   ```javascript
   POST /api/payment/process/
   ```

   **Request Body:**
   ```json
   {
     "orderId": "ORDER-1764174574974-8eqdp3m4l",
     "cardDetails": {
       "name": "John Doe",
       "number": "4111111111111111",
       "month": "12",
       "year": "2025",
       "cvc": "123"
     },
     "amount": 25500,  // in halalas (255.00 SAR)
     "description": "Wireless Bluetooth Headphones - Offer Accepted",
     "metadata": {
       "locale": "en",
       "product": "Wireless Bluetooth Headphones",
       "offerId": "6926e5cf2383d7ef4a6aae2f",
       "offerPrice": "240",
       "shipping": "15",
       "size": "",
       "price": "260"
     }
   }
   ```

---

### 3. **Payment Process API** (`/api/payment/process/`)
**File:** `app/api/payment/process/route.ts`

**Purpose:** Creates payment with Moyasar payment gateway.

**Process:**

1. **Receives Request:**
   - Extracts `orderId`, `cardDetails`, `amount`, `description`, `metadata`

2. **Converts Amount:**
   - If amount >= 1000, assumes already in halalas
   - Otherwise, converts SAR to halalas (multiply by 100)

3. **Prepares Payment Source:**
   - Uses card details directly (no token creation)
   - Formats as:
     ```json
     {
       "type": "creditcard",
       "name": "John Doe",
       "number": "4111111111111111",
       "month": "12",
       "year": "2025",
       "cvc": "123"
     }
     ```

4. **Creates Callback URL:**
   ```
   http://localhost:3000/en/payment/callback?offerId=...&product=...&offerPrice=...&shipping=...
   ```

5. **Calls Moyasar API:**
   ```javascript
   POST https://api.moyasar.com/v1/payments
   ```
   
   **Request:**
   ```json
   {
     "amount": 25500,
     "currency": "SAR",
     "description": "Wireless Bluetooth Headphones - Offer Accepted",
     "callback_url": "http://localhost:3000/en/payment/callback?...",
     "source": {
       "type": "creditcard",
       "name": "John Doe",
       "number": "4111111111111111",
       "month": "12",
       "year": "2025",
       "cvc": "123"
     },
     "metadata": { ... }
   }
   ```

6. **Returns Response:**
   ```json
   {
     "success": true,
     "payment": {
       "id": "16318f0e-c678-4476-b935-05639a48325d",
       "status": "initiated",  // or "paid" if no 3DS required
       "amount": 25500,
       "source": {
         "transaction_url": "https://api.moyasar.com/v1/card_auth/.../prepare"  // if 3DS required
       },
       ...
     },
     "orderId": "ORDER-1764174574974-8eqdp3m4l"
   }
   ```

---

### 4. **Payment Page - Handle Response**

**Two Scenarios:**

#### Scenario A: 3DS Required (`status: "initiated"`)

1. **Store Payment Data:**
   ```javascript
   sessionStorage.setItem('pendingPayment', JSON.stringify({
     orderId: orderId,
     paymentId: payment.id,
     offerId: offerId,
     product: product,
     size: size,
     price: price,
     offerPrice: offerPrice,
     shipping: shipping,
     totalPrice: totalPrice
   }));
   ```

2. **Redirect to 3DS Transaction URL:**
   ```javascript
   window.location.href = payment.source.transaction_url;
   ```
   - User completes 3DS authentication on Moyasar's page
   - After completion, Moyasar redirects to callback URL

#### Scenario B: No 3DS Required (`status: "paid"`)

1. **Save Payment to localStorage:**
   - Creates payment record with all details
   - Stores in `localStorage.getItem('payments')`

2. **Call Webhook:**
   ```javascript
   POST /api/payment/webhook/
   ```

3. **Redirect to Success Page:**
   ```
   /payment/success?offerId=...&product=...&offerPrice=...&shipping=...
   ```

---

### 5. **Payment Callback Page** (`/payment/callback`)
**File:** `app/[locale]/(dashboard)/payment/callback/page.tsx`

**Purpose:** Handles payment verification after 3DS completion.

**Process:**

1. **Extract Parameters:**
   - `paymentId` from URL (`?id=...`)
   - `offerId`, `product`, `offerPrice`, `shipping` from URL or sessionStorage

2. **Retrieve Pending Payment Data:**
   ```javascript
   const pendingPayment = JSON.parse(sessionStorage.getItem('pendingPayment'));
   ```

3. **Verify Payment Status (with Retry Logic):**
   ```javascript
   POST /api/payment/verify/
   ```
   
   **Request Body:**
   ```json
   {
     "paymentId": "16318f0e-c678-4476-b935-05639a48325d",
     "orderId": "ORDER-1764174574974-8eqdp3m4l",
     "offerId": "6926e5cf2383d7ef4a6aae2f"
   }
   ```
   
   **Retry Logic:**
   - Attempts up to 5 times
   - Waits 2 seconds between retries
   - Continues until status is `"paid"` or max retries reached

4. **If Payment is Paid:**
   - Save payment to localStorage
   - Call webhook API
   - Redirect to success page

5. **If Payment Still Initiated:**
   - Redirect back to payment page with error parameter

---

### 6. **Payment Verify API** (`/api/payment/verify/`)
**File:** `app/api/payment/verify/route.ts`

**Purpose:** Verifies payment status with Moyasar.

**Endpoints:**
- `GET /api/payment/verify?id=paymentId` (legacy)
- `POST /api/payment/verify/` (current)

**Process:**

1. **Receives Request:**
   ```json
   {
     "paymentId": "16318f0e-c678-4476-b935-05639a48325d",
     "orderId": "ORDER-...",
     "offerId": "6926e5cf..."
   }
   ```

2. **Calls Moyasar API:**
   ```javascript
   GET https://api.moyasar.com/v1/payments/{paymentId}
   ```
   
   **Headers:**
   ```
   Authorization: Basic {base64(SECRET_KEY + ':')}
   ```

3. **Returns Response:**
   ```json
   {
     "success": true,
     "payment": {
       "id": "16318f0e-c678-4476-b935-05639a48325d",
       "status": "paid",  // or "initiated", "failed", etc.
       "amount": 25500,
       "captured": 25500,
       "captured_at": "2025-11-26T16:29:38.125Z",
       ...
     },
     "orderId": "ORDER-...",
     "offerId": "6926e5cf..."
   }
   ```

---

### 7. **Payment Webhook API** (`/api/payment/webhook/`)
**File:** `app/api/payment/webhook/route.ts`

**Purpose:** Receives payment completion notification (called after successful payment).

**Called From:**
- Payment page (if no 3DS required)
- Payment callback page (after 3DS verification)

**Process:**

1. **Receives Request:**
   ```json
   {
     "id": "16318f0e-c678-4476-b935-05639a48325d",
     "status": "paid",
     "amount": 25500,
     "offerId": "6926e5cf2383d7ef4a6aae2f"
   }
   ```

2. **Validates Required Fields:**
   - `id` (payment ID)
   - `status` (payment status)
   - `amount` (payment amount)

3. **Logs Webhook Data:**
   - Payment ID
   - Status
   - Amount (in halalas and SAR)
   - Offer ID
   - Timestamp

4. **Returns Response:**
   ```json
   {
     "success": true,
     "message": "Webhook processed successfully",
     "data": {
       "id": "16318f0e-c678-4476-b935-05639a48325d",
       "status": "paid",
       "amount": 25500,
       "offerId": "6926e5cf2383d7ef4a6aae2f",
       "processedAt": "2025-11-26T16:29:38.153Z"
     }
   }
   ```

**Note:** This endpoint can be extended to:
- Update database records
- Send notifications
- Update order status
- Trigger other workflows

---

### 8. **Payment Success Page** (`/payment/success`)
**File:** `app/[locale]/(dashboard)/payment/success/page.tsx`

**Purpose:** Displays payment success confirmation.

**Process:**
- Shows success message
- Displays order details
- Provides "Continue Shopping" button

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/api/payment/process/` | POST | Create payment with Moyasar | `orderId`, `cardDetails`, `amount`, `description`, `metadata` | `{ success, payment, orderId }` |
| `/api/payment/verify/` | POST | Verify payment status | `{ paymentId, orderId?, offerId? }` | `{ success, payment, orderId?, offerId? }` |
| `/api/payment/webhook/` | POST | Receive payment completion notification | `{ id, status, amount, offerId? }` | `{ success, message, data }` |

---

## Data Flow

### Payment Data Storage

1. **SessionStorage** (temporary, for 3DS flow):
   ```javascript
   {
     orderId: "ORDER-...",
     paymentId: "16318f0e-...",
     offerId: "6926e5cf...",
     product: "Wireless Bluetooth Headphones",
     size: "",
     price: "260",
     offerPrice: "240",
     shipping: "15",
     totalPrice: "255.00"
   }
   ```

2. **LocalStorage** (persistent, for dashboard):
   ```javascript
   {
     id: "PAY-1764174574974",
     offerId: "6926e5cf...",
     product: "Wireless Bluetooth Headphones",
     size: "",
     price: "260",
     offerPrice: "240",
     shipping: "15",
     totalPrice: "255.00",
     affiliateCode: "",
     status: "ready",
     orderDate: "2025-11-26",
     paymentId: "16318f0e-...",
     paymentStatus: "paid",
     tokenData: { ... },
     paymentMethod: "card"
   }
   ```

---

## Error Handling

### Payment Process Errors
- Invalid card details → Error message displayed
- Insufficient funds → Moyasar API error returned
- Network errors → User-friendly error message

### 3DS Errors
- Payment still initiated after retries → Redirect to payment page with error
- Payment verification failed → Redirect to payment page with error
- Payment cancelled → Redirect to payment page

### Webhook Errors
- Webhook failures are logged but don't block payment success
- Payment is still saved to localStorage even if webhook fails

---

## Security Considerations

1. **Secret Key:** Only used on backend (never exposed to frontend)
2. **Card Details:** Sent directly to Moyasar API (not stored)
3. **Payment Tokens:** Generated by Moyasar (secure)
4. **3DS Authentication:** Handled by Moyasar (PCI compliant)

---

## Testing

### Test Card Numbers (Moyasar Test Mode)
- Success: `4111111111111111`
- 3DS Required: Most cards in test mode
- Decline: `4000000000000002`

### Test Flow
1. Use test card number
2. Complete checkout form
3. Submit payment
4. Complete 3DS (if required)
5. Verify payment in dashboard

---

## Notes

- All amounts are in **halalas** (smallest currency unit: 1 SAR = 100 halalas)
- Payment status can be: `initiated`, `paid`, `failed`, `refunded`
- 3DS is required for most cards in Saudi Arabia (Mada cards)
- Callback URL must be accessible from the internet (for production)
- Webhook can be extended to update backend database/offer status

