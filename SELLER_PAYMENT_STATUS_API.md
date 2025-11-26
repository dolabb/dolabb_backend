# Seller Payment Status API Guide

## Overview

Sellers can check the payment status of their products through multiple APIs. This guide explains all available endpoints and how to use them.

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

## API Endpoints for Payment Status

### 1. Get Accepted/Paid Offers (Recommended for Offer-Based Sales)

**Endpoint:** `GET /api/offers/accepted/`

**Description:** Get all accepted and paid offers with detailed payment and order information. This is the **best API for sellers** to check payment status for offer-based sales.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "offers": [
    {
      "id": "offer_id",
      "product": {
        "id": "product_id",
        "title": "Product Title",
        "images": ["https://example.com/image.jpg"],
        "price": 99.99,
        "originalPrice": 120.0,
        "currency": "SAR"
      },
      "buyer": {
        "id": "buyer_id",
        "name": "Buyer Name",
        "email": "buyer@example.com",
        "phone": "+1234567890"
      },
      "offerAmount": 80.0,
      "originalPrice": 99.99,
      "shippingCost": 10.0,
      "shippingAddress": "123 Main St",
      "zipCode": "12345",
      "houseNumber": "Apt 4B",
      "status": "paid",
      "paymentStatus": "completed",
      "isPaidOnMoyasar": true,
      "moyasarPaymentId": "payment_id",
      "orderId": "order_id",
      "orderStatus": "packed",
      "shipmentProof": null,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

**Key Fields:**
- `status`: Offer status (`"accepted"` or `"paid"`)
- `paymentStatus`: Payment status (`"not_paid"`, `"pending"`, `"completed"`, `"failed"`)
- `isPaidOnMoyasar`: Boolean indicating if payment is completed
- `moyasarPaymentId`: Moyasar payment ID (if payment completed)
- `orderId`: Associated order ID
- `orderStatus`: Order status (`"pending"`, `"packed"`, `"ready"`, `"shipped"`, `"delivered"`, `"cancelled"`)

**Payment Status Values:**
- `not_paid` - No payment made yet
- `pending` - Payment is pending
- `completed` - Payment completed ✅
- `failed` - Payment failed

---

### 2. Get Specific Accepted/Paid Offer Detail

**Endpoint:** `GET /api/offers/accepted/{offer_id}/`

**Description:** Get detailed information about a specific accepted or paid offer.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "offer": {
    "id": "offer_id",
    "product": {
      "id": "product_id",
      "title": "Product Title",
      "description": "Product description",
      "images": ["https://example.com/image.jpg"],
      "price": 99.99,
      "originalPrice": 120.0,
      "currency": "SAR",
      "category": "women",
      "condition": "new"
    },
    "buyer": {
      "id": "buyer_id",
      "name": "Buyer Name",
      "email": "buyer@example.com",
      "phone": "+1234567890",
      "profileImage": "https://example.com/profile.jpg"
    },
    "offerAmount": 80.0,
    "originalPrice": 99.99,
    "shippingCost": 10.0,
    "shippingAddress": "123 Main St",
    "zipCode": "12345",
    "houseNumber": "Apt 4B",
    "status": "paid",
    "paymentStatus": "completed",
    "isPaidOnMoyasar": true,
    "moyasarPaymentId": "payment_id",
    "order": {
      "id": "order_id",
      "orderNumber": "ORD-ABC123XYZ",
      "status": "packed",
      "trackingNumber": null,
      "shipmentProof": null
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

---

### 3. Get User Orders/Payments (For All Sales)

**Endpoint:** `GET /api/user/orders/` or `GET /api/user/payments/`

**Description:** Get all orders for the seller. When accessed by a seller, it returns as "payments" and includes payment status. This API works for both offer-based and direct purchases.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): Filter by order status (`pending`, `packed`, `ready`, `shipped`, `delivered`, `cancelled`)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
  "payments": [
    {
      "id": "order_id",
      "orderNumber": "ORD-ABC123XYZ",
      "product": {
        "id": "product_id",
        "title": "Product Title",
        "images": ["https://example.com/image.jpg"]
      },
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "profileImage": "https://example.com/profile.jpg"
      },
      "orderDate": "2024-01-01T00:00:00Z",
      "status": "packed",
      "paymentStatus": "completed",
      "totalPrice": 109.99,
      "platformFee": 5.5,
      "sellerPayout": 104.49,
      "affiliateCode": "AFF123",
      "paymentId": "moyasar_payment_id",
      "shippingAddress": {
        "fullName": "John Doe",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "New York",
        "postalCode": "10001",
        "country": "US",
        "additionalInfo": "Apt 4B"
      },
      "trackingNumber": ""
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50
  }
}
```

**Key Fields:**
- `paymentStatus`: Payment status (`"pending"`, `"completed"`, `"failed"`)
- `status`: Order status
- `paymentId`: Moyasar payment ID (if payment completed)
- `sellerPayout`: Amount seller will receive after fees
- `platformFee`: Platform fee deducted

**Payment Status Values:**
- `pending` - Payment is pending
- `completed` - Payment completed ✅
- `failed` - Payment failed

---

## Frontend Implementation Examples

### React/TypeScript Example

```typescript
// Get accepted/paid offers with payment status
async function getAcceptedOffers(token: string) {
  const response = await fetch(
    'https://dolabb-backend-2vsj.onrender.com/api/offers/accepted/',
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  const data = await response.json();
  return data;
}

// Get all orders/payments
async function getSellerPayments(
  token: string,
  status?: string,
  page: number = 1,
  limit: number = 20
) {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  
  if (status) {
    params.append('status', status);
  }

  const response = await fetch(
    `https://dolabb-backend-2vsj.onrender.com/api/user/payments/?${params}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  const data = await response.json();
  return data;
}

// React Component Example
function SellerPaymentsList({ token }: { token: string }) {
  const [offers, setOffers] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch both offers and orders
        const [offersData, paymentsData] = await Promise.all([
          getAcceptedOffers(token),
          getSellerPayments(token),
        ]);

        if (offersData.success) {
          setOffers(offersData.offers);
        }

        if (paymentsData.payments) {
          setPayments(paymentsData.payments);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [token]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Accepted Offers</h2>
      {offers.map((offer: any) => (
        <div key={offer.id}>
          <h3>{offer.product.title}</h3>
          <p>Offer Status: {offer.status}</p>
          <p>Payment Status: {offer.paymentStatus}</p>
          {offer.paymentStatus === 'completed' && (
            <p>✅ Payment Completed - Moyasar ID: {offer.moyasarPaymentId}</p>
          )}
        </div>
      ))}

      <h2>All Orders/Payments</h2>
      {payments.map((payment: any) => (
        <div key={payment.id}>
          <h3>{payment.product.title}</h3>
          <p>Order: {payment.orderNumber}</p>
          <p>Payment Status: {payment.paymentStatus}</p>
          <p>Seller Payout: ${payment.sellerPayout}</p>
        </div>
      ))}
    </div>
  );
}
```

### Filter by Payment Status

```typescript
// Filter offers by payment status
function filterOffersByPaymentStatus(offers: any[], status: string) {
  return offers.filter(offer => offer.paymentStatus === status);
}

// Get only paid offers
const paidOffers = filterOffersByPaymentStatus(offers, 'completed');

// Get pending payments
const pendingOffers = filterOffersByPaymentStatus(offers, 'pending');
```

---

## Payment Status Flow

### For Offer-Based Sales:

1. **Offer Created** → `status: "pending"`
2. **Seller Accepts** → `status: "accepted"`, `paymentStatus: "not_paid"`
3. **Buyer Pays** → `status: "paid"`, `paymentStatus: "completed"`
4. **Order Created** → `orderStatus: "packed"`

### For Direct Purchases:

1. **Order Created** → `paymentStatus: "pending"`
2. **Buyer Pays** → `paymentStatus: "completed"`
3. **Order Status** → `status: "packed"`

---

## Best Practices

### 1. Use the Right API

- **For Offer-Based Sales**: Use `/api/offers/accepted/` - Most detailed information
- **For All Sales**: Use `/api/user/payments/` - Comprehensive view of all orders

### 2. Check Payment Status

Always check both:
- `paymentStatus` - Current payment state
- `status` (for offers) - Offer state (`"paid"` means payment completed)

### 3. Display Payment Status

```typescript
function getPaymentStatusBadge(paymentStatus: string) {
  switch (paymentStatus) {
    case 'completed':
      return { text: 'Paid', color: 'green', icon: '✅' };
    case 'pending':
      return { text: 'Pending', color: 'yellow', icon: '⏳' };
    case 'failed':
      return { text: 'Failed', color: 'red', icon: '❌' };
    case 'not_paid':
      return { text: 'Not Paid', color: 'gray', icon: '⭕' };
    default:
      return { text: 'Unknown', color: 'gray', icon: '❓' };
  }
}
```

### 4. Real-time Updates

Consider polling the API or using WebSocket to get real-time payment status updates:

```typescript
// Poll every 30 seconds for payment status updates
useEffect(() => {
  const interval = setInterval(async () => {
    const data = await getAcceptedOffers(token);
    setOffers(data.offers);
  }, 30000);

  return () => clearInterval(interval);
}, [token]);
```

---

## Summary

**Sellers can check payment status through:**

1. ✅ **`GET /api/offers/accepted/`** - Best for offer-based sales (includes detailed payment info)
2. ✅ **`GET /api/offers/accepted/{offer_id}/`** - Get specific offer details
3. ✅ **`GET /api/user/payments/`** - Get all orders/payments (includes payment status)

**Payment Status Values:**
- `pending` - Payment is pending
- `completed` - Payment completed ✅
- `failed` - Payment failed
- `not_paid` - No payment made yet (for offers)

**Key Fields to Check:**
- `paymentStatus` - Current payment state
- `status` - Offer status (`"paid"` = payment completed)
- `isPaidOnMoyasar` - Boolean indicating payment completion
- `moyasarPaymentId` - Payment transaction ID

---

## Support

For API support or questions, contact the development team.

**Base URL:** `https://dolabb-backend-2vsj.onrender.com`

