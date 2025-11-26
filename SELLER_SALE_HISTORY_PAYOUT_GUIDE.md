# Seller Guide: Sale History & Payout Management

## Overview

This guide documents the APIs and functionality for sellers to view their sale
history and manage payouts. Sellers can access these features through the
Profile page under "Sale History" and "Payout" tabs.

---

## Base URL

```
https://dolabb-backend-2vsj.onrender.com
```

## Authentication

All endpoints require JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Part 1: Sale History

### API Endpoint: Get Seller Payments (Sale History)

**Endpoint:** `GET /api/user/payments/`

**Purpose:** Retrieve all payments/sales for the authenticated seller. This
shows the complete sale history including order details, buyer information,
platform fees, and seller payout amounts.

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 10)
- `status` (optional): Filter by order status (`pending`, `paid`, `shipped`,
  `delivered`, `cancelled`)

**Example Request:**

```javascript
GET /api/user/payments/?page=1&limit=10
```

**Response (200 OK):**

```json
{
  "payments": [
    {
      "id": "payment_id",
      "orderNumber": "ORD-12345",
      "product": {
        "id": "product_id",
        "title": "Vintage Denim Jacket",
        "images": [
          "https://example.com/image1.jpg",
          "https://example.com/image2.jpg"
        ]
      },
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "profileImage": "https://example.com/profile.jpg"
      },
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "profileImage": "https://example.com/seller.jpg"
      },
      "orderDate": "2024-01-15T10:30:00Z",
      "status": "delivered",
      "totalPrice": 150.0,
      "platformFee": 15.0,
      "sellerPayout": 135.0,
      "affiliateCode": "AFF123",
      "shippingAddress": {
        "fullName": "John Doe",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "Riyadh",
        "postalCode": "12345",
        "country": "Saudi Arabia",
        "additionalInfo": "Apt 4B"
      },
      "trackingNumber": "TRACK123456"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 47
  }
}
```

**Key Fields:**

- `id`: Payment/Order ID
- `orderNumber`: Human-readable order number
- `product`: Product details (id, title, images)
- `buyer`: Buyer information (id, username, profileImage)
- `seller`: Seller information (id, username, profileImage)
- `orderDate`: When the order was placed
- `status`: Order status (`pending`, `paid`, `shipped`, `delivered`,
  `cancelled`)
- `totalPrice`: Total order amount (buyer paid)
- `platformFee`: Platform commission fee
- `sellerPayout`: Amount seller receives (totalPrice - platformFee)
- `affiliateCode`: Affiliate code used (if any)
- `shippingAddress`: Complete shipping address
- `trackingNumber`: Shipping tracking number (if shipped)

**Frontend Implementation:**

- Component: `components/dashboard/SaleHistoryTab.tsx`
- Hook: `useGetPaymentsQuery` from `lib/api/ordersApi.ts`
- Displays: Product image, order number, date, buyer name, total price, platform
  fee, seller payout, and order status

---

## Part 2: Payout Management

### 2.1 Get Seller Earnings Summary

**Endpoint:** `GET /api/seller/earnings/`

**Purpose:** Get summary of seller earnings including total earnings, total
payouts, pending payouts, and available balance.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

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

**Key Fields:**

- `totalEarnings`: Sum of all seller payouts from completed sales
- `totalPayouts`: Sum of all approved payout requests
- `pendingPayouts`: Sum of all pending payout requests
- `availableBalance`: Amount available for payout (totalEarnings -
  totalPayouts - pendingPayouts)

**Frontend Implementation:**

- Component: `components/dashboard/PayoutTab.tsx`
- Hook: `useGetSellerEarningsQuery` from `lib/api/sellerApi.ts`
- Fallback: If API unavailable, calculates from payments data

---

### 2.2 Request Payout

**Endpoint:** `POST /api/seller/payout/request/`

**Purpose:** Submit a payout request to withdraw available balance.

**Headers:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "amount": 500.0,
  "paymentMethod": "Bank Transfer"
}
```

**Payment Methods:**

- `Bank Transfer`
- `PayPal`
- `Stripe`

**Response (200 OK):**

```json
{
  "success": true,
  "payoutRequest": {
    "id": "payout_request_id",
    "sellerId": "seller_id",
    "amount": 500.0,
    "status": "pending",
    "paymentMethod": "Bank Transfer",
    "requestedAt": "2024-01-15T10:30:00Z",
    "processedAt": null,
    "notes": null
  }
}
```

**Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Amount exceeds available balance"
}
```

**Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Invalid amount. Amount must be greater than 0"
}
```

**Frontend Implementation:**

- Component: `components/dashboard/PayoutTab.tsx`
- Hook: `useRequestSellerPayoutMutation` from `lib/api/sellerApi.ts`
- Validation: Checks amount > 0 and amount <= availableBalance

---

### 2.3 Get Payout Requests History

**Endpoint:** `GET /api/seller/payout-requests/`

**Purpose:** Get list of all payout requests for the authenticated seller.

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`)

**Example Request:**

```javascript
GET /api/seller/payout-requests/?page=1&limit=20&status=pending
```

**Response (200 OK):**

```json
{
  "success": true,
  "payoutRequests": [
    {
      "id": "payout_request_id_1",
      "sellerId": "seller_id",
      "amount": 500.0,
      "status": "pending",
      "paymentMethod": "Bank Transfer",
      "requestedAt": "2024-01-15T10:30:00Z",
      "processedAt": null,
      "notes": null
    },
    {
      "id": "payout_request_id_2",
      "sellerId": "seller_id",
      "amount": 1000.0,
      "status": "approved",
      "paymentMethod": "PayPal",
      "requestedAt": "2024-01-10T08:00:00Z",
      "processedAt": "2024-01-12T14:30:00Z",
      "notes": "Payment processed successfully"
    },
    {
      "id": "payout_request_id_3",
      "sellerId": "seller_id",
      "amount": 200.0,
      "status": "rejected",
      "paymentMethod": "Bank Transfer",
      "requestedAt": "2024-01-05T12:00:00Z",
      "processedAt": "2024-01-06T09:00:00Z",
      "notes": "Invalid bank account details"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 2,
    "totalItems": 15
  }
}
```

**Key Fields:**

- `id`: Payout request ID
- `sellerId`: Seller ID
- `amount`: Requested payout amount
- `status`: Request status (`pending`, `approved`, `rejected`)
- `paymentMethod`: Payment method selected
- `requestedAt`: When the request was submitted
- `processedAt`: When the request was processed (if approved/rejected)
- `notes`: Admin notes (if any)

**Frontend Implementation:**

- Component: `components/dashboard/PayoutTab.tsx`
- Hook: `useGetSellerPayoutRequestsQuery` from `lib/api/sellerApi.ts`
- Displays: Amount, payment method, request date, status with icons

---

## Frontend Components

### Sale History Tab

**Location:** `components/dashboard/SaleHistoryTab.tsx`

**Features:**

- Displays paginated list of all sales
- Shows product image, title, order number
- Displays buyer information
- Shows financial breakdown:
  - Total Price (what buyer paid)
  - Platform Fee
  - Seller Payout (what seller receives)
- Order status badges with color coding
- Pagination support

**API Used:**

- `GET /api/user/payments/` via `useGetPaymentsQuery`

---

### Payout Tab

**Location:** `components/dashboard/PayoutTab.tsx`

**Features:**

1. **Earnings Summary Cards:**

   - Total Earnings
   - Total Payouts
   - Pending Payouts
   - Available Balance

2. **Payout Request Form:**

   - Amount input with validation
   - Payment method selection (Bank Transfer, PayPal, Stripe)
   - Available balance display
   - Submit button with loading state

3. **Payout Requests History:**
   - List of all payout requests
   - Status indicators (Pending, Approved, Rejected)
   - Request dates and amounts
   - Payment methods

**APIs Used:**

- `GET /api/seller/earnings/` via `useGetSellerEarningsQuery`
- `GET /api/seller/payout-requests/` via `useGetSellerPayoutRequestsQuery`
- `POST /api/seller/payout/request/` via `useRequestSellerPayoutMutation`
- `GET /api/user/payments/` via `useGetPaymentsQuery` (fallback for earnings
  calculation)

**Fallback Behavior:**

- If earnings API is unavailable, calculates earnings from payments data
- Sums up `sellerPayout` from all payments to get total earnings

---

## Error Handling

### Common Errors

**401 Unauthorized:**

```json
{
  "error": "Authentication required"
}
```

**Solution:** Ensure valid JWT token is included in Authorization header.

**400 Bad Request:**

```json
{
  "error": "Amount exceeds available balance"
}
```

**Solution:** Request amount must be <= availableBalance.

**404 Not Found:**

```json
{
  "error": "No payments found"
}
```

**Solution:** Seller has no sales yet.

**500 Internal Server Error:**

```json
{
  "error": "Internal server error"
}
```

**Solution:** Backend issue, contact support.

---

## Data Flow

### Sale History Flow:

1. User navigates to Profile → Sale History tab
2. Frontend calls `GET /api/user/payments/`
3. Backend returns seller's payment history
4. Frontend displays payments with pagination

### Payout Flow:

1. User navigates to Profile → Payout tab
2. Frontend calls `GET /api/seller/earnings/` to show summary
3. Frontend calls `GET /api/seller/payout-requests/` to show history
4. User enters amount and selects payment method
5. Frontend validates: amount > 0 and amount <= availableBalance
6. Frontend calls `POST /api/seller/payout/request/`
7. Backend creates payout request with status "pending"
8. Frontend refreshes payout requests list
9. Admin reviews and approves/rejects request
10. Seller sees updated status in payout requests history

---

## TypeScript Interfaces

### Payment Interface

```typescript
export interface Payment extends Order {
  buyer: {
    id: string;
    username: string;
    profileImage?: string;
  };
  platformFee: number;
  sellerPayout: number;
  affiliateCode?: string;
}
```

### Seller Earnings Interface

```typescript
export interface SellerEarnings {
  totalEarnings: number;
  totalPayouts: number;
  pendingPayouts: number;
  availableBalance: number;
}
```

### Payout Request Interface

```typescript
export interface SellerPayoutRequest {
  id: string;
  sellerId: string;
  amount: number;
  status: 'pending' | 'approved' | 'rejected';
  paymentMethod: string;
  requestedAt: string;
  processedAt?: string;
  notes?: string;
}
```

---

## Testing

### Test Sale History:

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/user/payments/?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Get Earnings:

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/seller/earnings/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Request Payout:

```bash
curl -X POST "https://dolabb-backend-2vsj.onrender.com/api/seller/payout/request/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "paymentMethod": "Bank Transfer"
  }'
```

### Test Get Payout Requests:

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/seller/payout-requests/?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Notes

1. **Earnings Calculation:** If the earnings API is not available, the frontend
   calculates earnings from payments data by summing all `sellerPayout` values.

2. **Payout Validation:** The frontend validates that:

   - Amount > 0
   - Amount <= availableBalance
   - Payment method is selected

3. **Status Flow:** Payout requests start as "pending", then are either
   "approved" or "rejected" by admin.

4. **Pagination:** Both sale history and payout requests support pagination for
   better performance with large datasets.

5. **Real-time Updates:** After submitting a payout request, the frontend
   automatically refreshes the payout requests list to show the new request.

---

## Summary

**Sale History APIs:**

- `GET /api/user/payments/` - Get seller's payment/sale history

**Payout APIs:**

- `GET /api/seller/earnings/` - Get earnings summary
- `POST /api/seller/payout/request/` - Request a payout
- `GET /api/seller/payout-requests/` - Get payout requests history

**Frontend Components:**

- `SaleHistoryTab.tsx` - Displays sale history
- `PayoutTab.tsx` - Manages payouts and shows earnings

**Location in UI:**

- Profile Page → Sale History Tab (for sellers)
- Profile Page → Payout Tab (for sellers)
