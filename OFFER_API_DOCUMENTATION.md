# Offer API Documentation

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

## 1. Create Offer

**Endpoint:** `POST /api/offers/create/`

**Headers:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "productId": "product_id",
  "offerAmount": 80.0,
  "shippingAddress": "123 Main St, City, Country",
  "zipCode": "12345",
  "houseNumber": "Apt 4B"
}
```

**Note:** `shippingAddress`, `zipCode`, and `houseNumber` are optional.

**Response (201 Created):**

```json
{
  "success": true,
  "offer": {
    "id": "offer_id",
    "productId": "product_id",
    "buyerId": "buyer_id",
    "offerAmount": 80.0,
    "shippingAddress": "123 Main St, City, Country",
    "zipCode": "12345",
    "houseNumber": "Apt 4B",
    "status": "pending",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## 2. Get Offers

**Endpoint:** `GET /api/offers/`

**Headers:**

```
Authorization: Bearer <token>
```

**Description:** Returns all offers for the authenticated user (as buyer or
seller).

**Response (200 OK):**

```json
{
  "success": true,
  "offers": [
    {
      "id": "offer_id",
      "productId": "product_id",
      "productTitle": "Product Title",
      "buyerId": "buyer_id",
      "buyerName": "Buyer Name",
      "sellerId": "seller_id",
      "sellerName": "Seller Name",
      "offerAmount": 80.0,
      "originalPrice": 99.99,
      "shippingCost": 10.0,
      "shippingAddress": "123 Main St",
      "zipCode": "12345",
      "houseNumber": "Apt 4B",
      "status": "pending",
      "expirationDate": "2024-01-08T00:00:00Z",
      "counterOfferAmount": null,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Status Values:**

- `pending` - Offer is waiting for seller response
- `accepted` - Offer has been accepted by seller
- `paid` - Payment has been completed (NEW)
- `rejected` - Offer has been rejected
- `countered` - Seller made a counter offer
- `expired` - Offer has expired

---

## 3. Accept Offer

**Endpoint:** `PUT /api/offers/{offer_id}/accept/`

**Headers:**

```
Authorization: Bearer <token>
```

**Description:** Seller accepts a pending offer.

**Response (200 OK):**

```json
{
  "success": true,
  "offer": {
    "id": "offer_id",
    "status": "accepted"
  }
}
```

**Error Response (404 Not Found):**

```json
{
  "success": false,
  "error": "Offer not found"
}
```

---

## 4. Reject Offer

**Endpoint:** `PUT /api/offers/{offer_id}/reject/`

**Headers:**

```
Authorization: Bearer <token>
```

**Description:** Seller rejects an offer.

**Response (200 OK):**

```json
{
  "success": true,
  "offer": {
    "id": "offer_id",
    "status": "rejected"
  }
}
```

---

## 5. Counter Offer

**Endpoint:** `POST /api/offers/{offer_id}/counter/`

**Headers:**

```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "counterAmount": 85.0
}
```

**Description:** Seller makes a counter offer with a different price.

**Response (200 OK):**

```json
{
  "success": true,
  "offer": {
    "id": "offer_id",
    "status": "countered",
    "counterOfferAmount": 85.0
  }
}
```

---

## 6. Get Accepted Offers (Seller Only)

**Endpoint:** `GET /api/offers/accepted/`

**Headers:**

```
Authorization: Bearer <token>
```

**Description:** Get all accepted and paid offers for the seller with payment
and order details.

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

**Status Field Values:**

- `accepted` - Offer accepted, payment pending
- `paid` - Payment completed (NEW)

**Payment Status Values:**

- `not_paid` - No payment made yet
- `pending` - Payment is pending
- `completed` - Payment completed
- `failed` - Payment failed

**Order Status Values:**

- `pending` - Order created, waiting for payment
- `packed` - Payment completed, order packed
- `ready` - Order ready for shipment
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled

---

## 7. Get Accepted Offer Detail (Seller Only)

**Endpoint:** `GET /api/offers/accepted/{offer_id}/`

**Headers:**

```
Authorization: Bearer <token>
```

**Description:** Get detailed information about a specific accepted or paid
offer.

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

**Error Response (404 Not Found):**

```json
{
  "success": false,
  "error": "Offer not found or not accepted"
}
```

---

## 8. Upload Shipment Proof

**Endpoint:** `POST /api/offers/accepted/{offer_id}/upload-shipment-proof/`

**Headers:**

```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Description:** Upload shipment proof image and update order status to
"delivered". Only works for offers with status "paid" or orders with
payment_status "completed".

**Request Body (Form Data):**

```
shipmentProof: <file>  // Image file (JPEG, PNG, GIF, WebP)
```

**OR**

**Request Body (JSON):**

```json
{
  "shipmentProofUrl": "https://example.com/shipment-proof.jpg"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Shipment proof uploaded and order status updated to Delivered",
  "order": {
    "id": "order_id",
    "orderNumber": "ORD-ABC123XYZ",
    "status": "delivered",
    "shipmentProof": "https://example.com/uploads/shipments/shipment_abc123.jpg"
  }
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Payment must be completed before uploading shipment proof"
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Shipment proof image is required. Use \"shipmentProof\" field for file upload or \"shipmentProofUrl\" for URL."
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Invalid file type. Only images (JPEG, PNG, GIF, WebP) are allowed."
}
```

---

## Frontend Integration Examples

### JavaScript/TypeScript Example

```typescript
const API_BASE_URL = 'https://dolabb-backend-2vsj.onrender.com';

// Get all accepted/paid offers
async function getAcceptedOffers(token: string) {
  const response = await fetch(`${API_BASE_URL}/api/offers/accepted/`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  return data;
}

// Get specific accepted/paid offer details
async function getAcceptedOfferDetail(token: string, offerId: string) {
  const response = await fetch(
    `${API_BASE_URL}/api/offers/accepted/${offerId}/`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  const data = await response.json();
  return data;
}

// Upload shipment proof
async function uploadShipmentProof(
  token: string,
  offerId: string,
  imageFile: File
) {
  const formData = new FormData();
  formData.append('shipmentProof', imageFile);

  const response = await fetch(
    `${API_BASE_URL}/api/offers/accepted/${offerId}/upload-shipment-proof/`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }
  );

  const data = await response.json();
  return data;
}

// Check if offer is paid
function isOfferPaid(offer: any): boolean {
  return offer.status === 'paid' || offer.paymentStatus === 'completed';
}
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function AcceptedOffersList({ token }) {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchOffers() {
      try {
        const response = await fetch(
          'https://dolabb-backend-2vsj.onrender.com/api/offers/accepted/',
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await response.json();
        if (data.success) {
          setOffers(data.offers);
        }
      } catch (error) {
        console.error('Error fetching offers:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchOffers();
  }, [token]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {offers.map(offer => (
        <div key={offer.id}>
          <h3>{offer.product.title}</h3>
          <p>Status: {offer.status}</p>
          <p>Payment Status: {offer.paymentStatus}</p>
          {offer.status === 'paid' && <p>✅ Payment Completed</p>}
        </div>
      ))}
    </div>
  );
}
```

---

## Important Notes

1. **Status Flow:**

   - `pending` → `accepted` (when seller accepts)
   - `accepted` → `paid` (when payment is completed via webhook or direct
     payment)

2. **Payment Status:**

   - The `status` field on the offer will be `'paid'` when payment is successful
   - The `paymentStatus` field shows the order's payment status
   - Both should be checked for accurate payment state

3. **Shipment Proof:**

   - Can only be uploaded for offers with `status: 'paid'` or
     `paymentStatus: 'completed'`
   - Uploading shipment proof automatically sets order status to `'delivered'`

4. **Error Handling:**
   - Always check the `success` field in responses
   - Handle 400, 404, and 500 status codes appropriately
   - Display user-friendly error messages from the `error` field

---

## Support

For API support or questions, contact the development team.

**Base URL:** `https://dolabb-backend-2vsj.onrender.com`
