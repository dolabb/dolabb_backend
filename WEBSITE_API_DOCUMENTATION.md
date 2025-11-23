# Dolabb Website API Documentation

## Base URL

```
https://dolabb-backend-2vsj.onrender.com
```

## Authentication

All authenticated endpoints require JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Table of Contents

1. [Authentication](#authentication-endpoints)
2. [Products](#products-endpoints)
3. [Offers](#offers-endpoints)
4. [Orders & Payments](#orders--payments-endpoints)
5. [Chat](#chat-endpoints)
6. [Notifications](#notifications-endpoints)
7. [State Management](#state-management-recommendations)
8. [Toast Messages](#toast-messages)

**Note:** For Affiliate API documentation, see
[AFFILIATE_API_DOCUMENTATION.md](./AFFILIATE_API_DOCUMENTATION.md)

---

## Authentication Endpoints

### 1. User Signup

**Endpoint:** `POST /api/auth/signup/`

**Request Body:**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "password123",
  "confirm_password": "password123",
  "country_code": "US",
  "dial_code": "+1",
  "profile_image_url": "https://example.com/image.jpg",
  "role": "buyer"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "message": "User registered successfully. OTP sent to email. Please verify OTP to complete registration.",
  "user": {
    "id": "user_id",
    "email": "john@example.com",
    "phone": "+1234567890",
    "profile_image": "",
    "role": "buyer",
    "status": "pending"
  },
  "otp": "1234"
}
```

**Toast Message:**
`"Registration successful! Please check your email for OTP verification."`

---

### 2. User Login

**Endpoint:** `POST /api/auth/login/`

**Request Body:**

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "user": {
    "id": "user_id",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "full_name": "John Doe",
    "profile_image": "https://example.com/image.jpg",
    "role": "buyer",
    "bio": "Bio text",
    "location": "New York",
    "country_code": "US",
    "dial_code": "+1",
    "status": "active",
    "join_date": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "jwt_token_here",
  "savedProducts": []
}
```

**Toast Message:** `"Welcome back, {full_name}!"`

---

### 3. Verify OTP (User)

**Endpoint:** `POST /api/auth/verify-otp/`

**Request Body:**

```json
{
  "email": "john@example.com",
  "otp": "1234"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user": {
    "id": "user_id",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "full_name": "John Doe",
    "profile_image": "https://example.com/image.jpg",
    "role": "buyer",
    "bio": "Bio text",
    "location": "New York",
    "country_code": "US",
    "dial_code": "+1",
    "status": "active",
    "join_date": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "jwt_token_here"
}
```

**Toast Message:** `"Email verified successfully! Your account is now active."`

---

### 4. Resend OTP

**Endpoint:** `POST /api/auth/resend-otp/`

**Request Body:**

```json
{
  "email": "john@example.com",
  "user_type": "user"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "OTP resent successfully",
  "otp": "5678"
}
```

**Toast Message:** `"OTP has been resent to your email."`

---

### 5. Forgot Password

**Endpoint:** `POST /api/auth/forgot-password/`

**Request Body:**

```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Reset OTP sent to email",
  "otp": "1234"
}
```

**Toast Message:** `"Password reset OTP sent to your email."`

---

### 6. Reset Password

**Endpoint:** `POST /api/auth/reset-password/`

**Request Body:**

```json
{
  "email": "john@example.com",
  "otp": "1234",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

**Toast Message:**
`"Password reset successfully! Please login with your new password."`

---

### 7. Get Profile

**Endpoint:** `GET /api/auth/profile/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "user": {
    "id": "user_id",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "full_name": "John Doe",
    "profile_image": "https://example.com/image.jpg",
    "bio": "Bio text",
    "location": "New York",
    "joined_date": "2024-01-01T00:00:00Z",
    "role": "buyer"
  }
}
```

---

### 8. Update Profile

**Endpoint:** `PUT /api/auth/profile/update/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "full_name": "John Updated",
  "username": "johndoe",
  "bio": "Updated bio",
  "location": "Los Angeles",
  "profile_image": "https://example.com/new-image.jpg"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "user": {
    "id": "user_id",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "full_name": "John Updated",
    "profile_image": "https://example.com/new-image.jpg",
    "bio": "Updated bio",
    "location": "Los Angeles",
    "joined_date": "2024-01-01T00:00:00Z",
    "role": "buyer"
  }
}
```

**Toast Message:** `"Profile updated successfully!"`

---

### 9. Upload Image

**Endpoint:** `POST /api/auth/upload-image/`

**Request:** `multipart/form-data`

- Field name: `image`
- Max size: 5MB
- Allowed types: JPEG, JPG, PNG, GIF, WEBP
- Validation: File extension and magic bytes validation to ensure valid image
  files

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "image_url": "https://dolabb-backend-2vsj.onrender.com/media/uploads/profiles/filename.jpg",
  "filename": "filename.jpg",
  "file_id": "file_id"
}
```

**Toast Message:** `"Image uploaded successfully!"`

---

## Products Endpoints

### 10. Get Products

**Endpoint:** `GET /api/products/`

**Query Parameters:**

- `category` (optional): Filter by category
- `subcategory` (optional): Filter by subcategory
- `brand` (optional): Filter by brand
- `minPrice` (optional): Minimum price
- `maxPrice` (optional): Maximum price
- `size` (optional): Filter by size
- `condition` (optional): Filter by condition
- `search` (optional): Search query
- `sortBy` (optional): `"newest"`, `"price: low to high"`,
  `"price: high to low"`, `"relevance"`
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200 OK):**

```json
[
  {
    "id": "product_id",
    "title": "Product Title",
    "description": "Product description",
    "price": 99.99,
    "originalPrice": 129.99,
    "images": ["https://example.com/image1.jpg"],
    "category": "Electronics",
    "subcategory": "Phones",
    "brand": "Apple",
    "size": "Large",
    "color": "Black",
    "condition": "new",
    "seller": {
      "id": "seller_id",
      "username": "seller_username",
      "profileImage": "https://example.com/profile.jpg"
    },
    "isSaved": false,
    "createdAt": "2024-01-01T00:00:00Z"
  }
]
```

---

### 11. Get Product Detail

**Endpoint:** `GET /api/products/{product_id}/`

**Response (200 OK):**

```json
{
  "id": "product_id",
  "title": "Product Title",
  "description": "Full product description",
  "price": 99.99,
  "originalPrice": 129.99,
  "images": ["https://example.com/image1.jpg"],
  "category": "Electronics",
  "subcategory": "Phones",
  "brand": "Apple",
  "size": "Large",
  "color": "Black",
  "condition": "new",
  "tags": ["tag1", "tag2"],
  "seller": {
    "id": "seller_id",
    "username": "seller_username",
    "profileImage": "https://example.com/profile.jpg",
    "rating": 0,
    "totalSales": 0
  },
  "likes": 10,
  "isLiked": false,
  "isSaved": false,
  "shippingInfo": {
    "cost": 10.0,
    "estimatedDays": 5,
    "locations": ["US", "CA"]
  },
  "createdAt": "2024-01-01T00:00:00Z",
  "affiliateCode": "AFF123"
}
```

---

### 12. Create Product

**Endpoint:** `POST /api/products/create/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "itemtitle": "Product Title",
  "description": "Product description",
  "price": 99.99,
  "originalPrice": 129.99,
  "category": "Electronics",
  "subcategory": "Phones",
  "brand": "Apple",
  "currency": "USD",
  "Quantity": 10,
  "Gender": "Unisex",
  "Size": "Large",
  "Color": "Black",
  "Condition": "new",
  "SKU/ID (Optional)": "SKU123",
  "Tags/Keywords": ["tag1", "tag2"],
  "Images": ["https://example.com/image1.jpg"],
  "Shipping Cost": 10.0,
  "Processing Time (days)": 5,
  "Shipping Locations": ["US", "CA"],
  "Affiliate Code (Optional)": "AFF123"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "product": {
    "id": "product_id",
    "itemtitle": "Product Title",
    "description": "Product description",
    "price": 99.99,
    "originalPrice": 129.99,
    "category": "Electronics",
    "subcategory": "Phones",
    "brand": "Apple",
    "currency": "USD",
    "Quantity": 10,
    "Gender": "Unisex",
    "Size": "Large",
    "Condition": "new",
    "SKU/ID (Optional)": "SKU123",
    "Tags/Keywords": ["tag1", "tag2"],
    "Images": ["https://example.com/image1.jpg"],
    "Shipping Cost": 10.0,
    "Processing Time (days)": 5,
    "Shipping Locations": ["US", "CA"],
    "status": "pending",
    "seller_id": "seller_id",
    "seller_name": "Seller Name",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Toast Message:** `"Product created successfully! Waiting for admin approval."`

---

### 13. Update Product

**Endpoint:** `PUT /api/products/{product_id}/update/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:** (Same as Create Product)

**Response (200 OK):**

```json
{
  "success": true,
  "product": {
    // Updated product object
  }
}
```

**Toast Message:** `"Product updated successfully!"`

---

### 14. Delete Product

**Endpoint:** `DELETE /api/products/{product_id}/delete/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

**Toast Message:** `"Product deleted successfully!"`

---

### 15. Get Seller Products

**Endpoint:** `GET /api/products/seller/`

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`)

**Response (200 OK):**

```json
[
  {
    "id": "product_id",
    "title": "Product Title",
    "description": "Product description",
    "price": 99.99,
    "originalPrice": 129.99,
    "images": ["https://example.com/image1.jpg"],
    "category": "Electronics",
    "subcategory": "Phones",
    "brand": "Apple",
    "size": "Large",
    "color": "Black",
    "condition": "new",
    "status": "approved",
    "approved": true,
    "quantity": 10,
    "isSaved": false,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
]
```

---

### 16. Save Product (Add to Wishlist)

**Endpoint:** `POST /api/products/{product_id}/save/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (201 Created):**

```json
{
  "success": true,
  "isSaved": true
}
```

**Toast Message:** `"Product added to wishlist!"`

---

### 17. Unsave Product (Remove from Wishlist)

**Endpoint:** `DELETE /api/products/{product_id}/unsave/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "isSaved": false
}
```

**Toast Message:** `"Product removed from wishlist!"`

---

### 18. Get Featured Products

**Endpoint:** `GET /api/products/featured/`

**Query Parameters:**

- `limit` (optional): Number of products (default: 10)
- `page` (optional): Page number (default: 1)

**Response (200 OK):**

```json
{
  "products": [
    {
      "id": "product_id",
      "title": "Product Title",
      "description": "Product description",
      "price": 99.99,
      "images": ["https://example.com/image1.jpg"],
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "profileImage": "https://example.com/profile.jpg"
      }
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50
  }
}
```

---

### 19. Get Trending Products

**Endpoint:** `GET /api/products/trending/`

**Query Parameters:**

- `limit` (optional): Number of products (default: 10)
- `page` (optional): Page number (default: 1)

**Response (200 OK):**

```json
{
  "products": [
    {
      "id": "product_id",
      "title": "Product Title",
      "description": "Product description",
      "price": 99.99,
      "images": ["https://example.com/image1.jpg"],
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "profileImage": "https://example.com/profile.jpg"
      }
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50
  }
}
```

---

## Offers Endpoints

### 20. Create Offer

**Endpoint:** `POST /api/offers/create/`

**Headers:**

```

```

Authorization: Bearer <token>

````

**Request Body:**

```json
{
  "productId": "product_id",
  "offerAmount": 80.0
}
````

**Response (201 Created):**

```json
{
  "success": true,
  "offer": {
    "id": "offer_id",
    "productId": "product_id",
    "buyerId": "buyer_id",
    "offerAmount": 80.0,
    "status": "pending",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

**Toast Message:**
`"Offer submitted successfully! Waiting for seller response."`

---

### 21. Get Offers

**Endpoint:** `GET /api/offers/`

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
      "productId": "product_id",
      "productTitle": "Product Title",
      "buyerId": "buyer_id",
      "buyerName": "Buyer Name",
      "sellerId": "seller_id",
      "sellerName": "Seller Name",
      "offerAmount": 80.0,
      "originalPrice": 99.99,
      "shippingCost": 10.0,
      "status": "pending",
      "expirationDate": "2024-01-08T00:00:00Z",
      "counterOfferAmount": null,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 22. Accept Offer

**Endpoint:** `PUT /api/offers/{offer_id}/accept/`

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
    "status": "accepted"
  }
}
```

**Toast Message:** `"Offer accepted! Order created successfully."`

---

### 23. Reject Offer

**Endpoint:** `PUT /api/offers/{offer_id}/reject/`

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
    "status": "rejected"
  }
}
```

**Toast Message:** `"Offer rejected."`

---

### 24. Counter Offer

**Endpoint:** `POST /api/offers/{offer_id}/counter/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "counterAmount": 85.0
}
```

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

**Toast Message:** `"Counter offer sent to buyer!"`

---

## Orders & Payments Endpoints

### 25. Get User Orders

**Endpoint:** `GET /api/user/orders/`

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `status` (optional): Filter by status
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200 OK):**

```json
{
  "orders": [
    {
      "id": "order_id",
      "orderNumber": "ORD123456",
      "product": {
        "id": "product_id",
        "title": "Product Title",
        "images": ["https://example.com/image1.jpg"]
      },
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "profileImage": "https://example.com/profile.jpg"
      },
      "orderDate": "2024-01-01T00:00:00Z",
      "status": "pending",
      "totalPrice": 109.99,
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

---

### 26. Get User Payments (Seller)

**Endpoint:** `GET /api/user/payments/`

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `status` (optional): Filter by status
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200 OK):**

```json
{
  "payments": [
    {
      "id": "order_id",
      "orderNumber": "ORD123456",
      "product": {
        "id": "product_id",
        "title": "Product Title",
        "images": ["https://example.com/image1.jpg"]
      },
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "profileImage": "https://example.com/profile.jpg"
      },
      "orderDate": "2024-01-01T00:00:00Z",
      "status": "pending",
      "totalPrice": 109.99,
      "platformFee": 5.5,
      "sellerPayout": 104.49,
      "affiliateCode": "AFF123",
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

---

### 27. Ship Order

**Endpoint:** `PUT /api/user/payments/{order_id}/ship/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "trackingNumber": "TRACK123456"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "payment": {
    "id": "order_id",
    "status": "shipped",
    "trackingNumber": "TRACK123456"
  }
}
```

**Toast Message:** `"Order shipped! Tracking number updated."`

---

### 28. Checkout (Create Order)

**Endpoint:** `POST /api/payment/checkout/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "productId": "product_id",
  "offerId": "offer_id",
  "quantity": 1,
  "shippingAddress": {
    "fullName": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "postalCode": "10001",
    "country": "US",
    "additionalInfo": "Apt 4B"
  },
  "affiliateCode": "AFF123"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "orderId": "order_id",
  "checkoutData": {
    "product": "Product Title",
    "size": "",
    "price": 99.99,
    "offerPrice": 80.0,
    "shipping": 10.0,
    "platformFee": 5.5,
    "affiliateCode": "AFF123",
    "total": 95.5
  }
}
```

**Toast Message:** `"Order created! Proceed to payment."`

---

### 29. Process Payment

**Endpoint:** `POST /api/payment/process/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "orderId": "order_id",
  "tokenId": "moyasar_token_id",
  "amount": 95.5,
  "description": "Order payment",
  "metadata": {
    "orderNumber": "ORD123456"
  }
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "payment": {
    "id": "payment_id",
    "status": "paid",
    "amount": 95.5,
    "currency": "SAR",
    "source": {
      "type": "creditcard",
      "company": "visa"
    },
    "order": {
      "id": "order_id",
      "orderNumber": "ORD123456"
    }
  }
}
```

**Toast Message:** `"Payment successful! Your order is confirmed."`

---

## Chat Endpoints

### 30. Get Conversations

**Endpoint:** `GET /api/chat/conversations/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "conversations": [
    {
      "id": "conversation_id",
      "participants": [
        {
          "id": "user_id",
          "username": "username",
          "profileImage": "https://example.com/profile.jpg"
        }
      ],
      "lastMessage": {
        "text": "Hello",
        "timestamp": "2024-01-01T00:00:00Z"
      },
      "unreadCount": 2,
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 31. Get Messages

**Endpoint:** `GET /api/chat/conversations/{conversation_id}/messages/`

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Response (200 OK):**

```json
{
  "success": true,
  "messages": [
    {
      "id": "message_id",
      "senderId": "sender_id",
      "receiverId": "receiver_id",
      "text": "Hello",
      "attachments": [],
      "productId": "product_id",
      "offerId": "offer_id",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50
  }
}
```

---

### 32. Send Message

**Endpoint:** `POST /api/chat/send/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "receiverId": "receiver_id",
  "text": "Hello, is this available?",
  "productId": "product_id",
  "attachments": [],
  "offerId": "offer_id"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "message": {
    "id": "message_id",
    "text": "Hello, is this available?",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

---

### 33. Upload File (Chat)

**Endpoint:** `POST /api/chat/upload/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request:** `multipart/form-data`

- Field name: `file`

**Response (201 Created):**

```json
{
  "success": true,
  "fileUrl": "https://dolabb-backend-2vsj.onrender.com/media/chat/filename.jpg"
}
```

---

## Notifications Endpoints

### 34. Get Notifications

**Endpoint:** `GET /api/notifications/`

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `isRead` (optional): Filter by read status (`true`/`false`)

**Response (200 OK):**

```json
{
  "success": true,
  "notifications": [
    {
      "id": "notification_id",
      "title": "New Order",
      "message": "You have a new order",
      "type": "order",
      "isRead": false,
      "createdAt": "2024-01-01T00:00:00Z",
      "link": "/orders/order_id"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50
  }
}
```

---

### 35. Mark Notification as Read

**Endpoint:** `PUT /api/notifications/{notification_id}/read/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

### 36. Mark All Notifications as Read

**Endpoint:** `PUT /api/notifications/mark-all-read/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

**Toast Message:** `"All notifications marked as read!"`

---

### 37. Delete Notification

**Endpoint:** `DELETE /api/notifications/{notification_id}/delete/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Notification deleted"
}
```

---

### 38. Bulk Delete Notifications

**Endpoint:** `POST /api/notifications/bulk-delete/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "notificationIds": ["notification_id1", "notification_id2"]
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Notifications deleted"
}
```

**Toast Message:** `"Notifications deleted successfully!"`

---

## State Management Recommendations

### Recommended Approach: Redux Toolkit + RTK Query

For a React/Next.js application, we recommend using **Redux Toolkit** with **RTK
Query** for the following reasons:

1. **Centralized State Management**:

   - User authentication state
   - Product listings and filters
   - Shopping cart/wishlist
   - Orders and payments
   - Chat conversations
   - Notifications

2. **RTK Query Benefits**:
   - Automatic caching
   - Request deduplication
   - Background refetching
   - Optimistic updates
   - Built-in loading/error states

### State Structure Example:

```typescript
// Store structure
{
  auth: {
    user: User | null,
    token: string | null,
    isAuthenticated: boolean,
    loading: boolean
  },
  products: {
    items: Product[],
    filters: FilterState,
    savedProducts: string[],
    currentProduct: Product | null
  },
  orders: {
    orders: Order[],
    currentOrder: Order | null
  },
  chat: {
    conversations: Conversation[],
    messages: Record<string, Message[]>,
    activeConversation: string | null
  },
  notifications: {
    items: Notification[],
    unreadCount: number
  },
  affiliate: {
    code: string | null,
    earnings: AffiliateEarnings | null
  }
}
```

### Alternative: Zustand (Lighter Option)

For smaller applications or if you prefer a simpler solution:

```typescript
// Zustand store example
import create from 'zustand';

const useStore = create(set => ({
  user: null,
  token: null,
  setAuth: (user, token) => set({ user, token }),
  clearAuth: () => set({ user: null, token: null }),
  // ... other state
}));
```

### API Client Setup (Axios Example):

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://dolabb-backend-2vsj.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## Toast Messages

### Success Messages

| Action                    | Message                                                                  |
| ------------------------- | ------------------------------------------------------------------------ |
| User Signup               | "Registration successful! Please check your email for OTP verification." |
| User Login                | "Welcome back, {full_name}!"                                             |
| OTP Verified              | "Email verified successfully! Your account is now active."               |
| OTP Resent                | "OTP has been resent to your email."                                     |
| Password Reset            | "Password reset successfully! Please login with your new password."      |
| Profile Updated           | "Profile updated successfully!"                                          |
| Image Uploaded            | "Image uploaded successfully!"                                           |
| Product Created           | "Product created successfully! Waiting for admin approval."              |
| Product Updated           | "Product updated successfully!"                                          |
| Product Deleted           | "Product deleted successfully!"                                          |
| Product Saved             | "Product added to wishlist!"                                             |
| Product Unsaved           | "Product removed from wishlist!"                                         |
| Offer Created             | "Offer submitted successfully! Waiting for seller response."             |
| Offer Accepted            | "Offer accepted! Order created successfully."                            |
| Counter Offer Sent        | "Counter offer sent to buyer!"                                           |
| Order Created             | "Order created! Proceed to payment."                                     |
| Payment Successful        | "Payment successful! Your order is confirmed."                           |
| Order Shipped             | "Order shipped! Tracking number updated."                                |
| Notifications Marked Read | "All notifications marked as read!"                                      |
| Notifications Deleted     | "Notifications deleted successfully!"                                    |

### Error Messages

| Error Type           | Message                                                               |
| -------------------- | --------------------------------------------------------------------- |
| Invalid Credentials  | "Invalid email or password. Please try again."                        |
| OTP Expired          | "OTP has expired. Please request a new one."                          |
| Invalid OTP          | "Invalid OTP. Please check and try again."                            |
| Email Already Exists | "This email is already registered. Please login instead."             |
| Password Mismatch    | "Passwords do not match. Please try again."                           |
| Network Error        | "Network error. Please check your connection and try again."          |
| Unauthorized         | "Session expired. Please login again."                                |
| Product Not Found    | "Product not found."                                                  |
| Insufficient Balance | "Insufficient balance for this transaction."                          |
| Payment Failed       | "Payment failed. Please try again or use a different payment method." |
| File Too Large       | "File size too large. Maximum size is 5MB."                           |
| Invalid File Type    | "Invalid file type. Please upload an image (JPEG, PNG, GIF, WEBP)."   |

### Info Messages

| Action             | Message                      |
| ------------------ | ---------------------------- |
| Loading            | "Please wait..."             |
| Processing Payment | "Processing your payment..." |
| Uploading Image    | "Uploading image..."         |

---

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

### HTTP Status Codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or token expired
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Handling Example:

```typescript
try {
  const response = await apiClient.post('/api/auth/login', credentials);
  if (response.data.success) {
    // Handle success
    toast.success('Welcome back!');
  }
} catch (error) {
  if (error.response?.status === 401) {
    toast.error('Invalid email or password. Please try again.');
  } else if (error.response?.status === 500) {
    toast.error('Server error. Please try again later.');
  } else {
    toast.error(error.response?.data?.error || 'An error occurred');
  }
}
```

---

## WebSocket Endpoints

### Chat WebSocket

**URL:** `wss://dolabb-backend-2vsj.onrender.com/ws/chat/{conversation_id}/`

**Connection:**

```javascript
const ws = new WebSocket(
  `wss://dolabb-backend-2vsj.onrender.com/ws/chat/${conversationId}/`
);
ws.onmessage = event => {
  const message = JSON.parse(event.data);
  // Handle message
};
```

### Notifications WebSocket

**URL:** `wss://dolabb-backend-2vsj.onrender.com/ws/notifications/{user_id}/`

**Connection:**

```javascript
const ws = new WebSocket(
  `wss://dolabb-backend-2vsj.onrender.com/ws/notifications/${userId}/`
);
ws.onmessage = event => {
  const notification = JSON.parse(event.data);
  // Handle notification
};
```

---

## Notes

1. **Token Storage**: Store JWT token in `localStorage` or `sessionStorage` for
   persistence
2. **Token Refresh**: Implement token refresh logic if tokens expire
3. **Image URLs**: All image URLs returned are absolute URLs
4. **Pagination**: All list endpoints support pagination with `page` and `limit`
   parameters
5. **Filtering**: Most list endpoints support filtering via query parameters
6. **Real-time Updates**: Use WebSocket connections for real-time chat and
   notifications
7. **Error Handling**: Always check `success` field in responses before
   processing data
8. **Loading States**: Show loading indicators during API calls
9. **Optimistic Updates**: Consider optimistic updates for better UX (e.g.,
   saving products)

---

## Support

For API support or questions, contact the development team.

**Base URL:** `https://dolabb-backend-2vsj.onrender.com`

---

## Related Documentation

- [Affiliate API Documentation](./AFFILIATE_API_DOCUMENTATION.md) - For
  affiliate-specific APIs
- [Admin Dashboard API Documentation](./ADMIN_DASHBOARD_API_DOCUMENTATION.md) -
  For admin-specific APIs
