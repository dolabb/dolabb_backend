# Buyer-Side Dispute API Guide

Complete guide for buyer-side dispute management functionality with all APIs, request/response examples, and workflow.

---

## Table of Contents
1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Complete Workflow Example](#complete-workflow-example)
6. [Error Handling](#error-handling)

---

## Overview

The buyer-side dispute system allows buyers to:
- Create disputes for orders they've placed
- View all their disputes
- View detailed information about a specific dispute
- Add comments/responses to their disputes
- Track dispute status and admin responses

**Dispute Types:**
- `product_quality` - Issues with product quality or condition
- `delivery_issue` - Problems with delivery or shipping
- `payment_dispute` - Payment-related issues

**Dispute Status:**
- `open` - Dispute is active and being reviewed
- `resolved` - Dispute has been resolved by admin
- `closed` - Dispute is closed (final state)

---

## Base URL

```
Production: https://dolabb-backend-2vsj.onrender.com
Development: http://localhost:8000
```

All buyer dispute endpoints are under: `/api/products/user/disputes/`

---

## Authentication

All endpoints require authentication. Include the authentication token in the request headers:

```
Authorization: Bearer <your_access_token>
```

**Note:** Only buyers can access these endpoints. The system automatically identifies the buyer from the authentication token.

---

## API Endpoints

### 1. Create Dispute

Create a new dispute for an order.

**Endpoint:** `POST /api/products/user/disputes/create/`

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "orderId": "507f1f77bcf86cd799439011",
  "disputeType": "product_quality",
  "description": "The product I received is damaged and not as described. The packaging was torn and the item inside is broken."
}
```

**Request Parameters:**
- `orderId` (required, string) - The MongoDB ObjectId of the order
- `disputeType` (required, string) - One of: `product_quality`, `delivery_issue`, `payment_dispute`
- `description` (required, string) - Detailed description of the dispute

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Dispute/report submitted successfully. Admin will review it.",
  "dispute": {
    "id": "507f191e810c19729de860ea",
    "caseNumber": "DISP-2024-0123",
    "type": "product_quality",
    "status": "open",
    "createdAt": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error Responses:**

**400 Bad Request - Missing Order ID:**
```json
{
  "success": false,
  "error": "Order ID is required"
}
```

**400 Bad Request - Invalid Dispute Type:**
```json
{
  "success": false,
  "error": "Invalid dispute type"
}
```

**400 Bad Request - Order Not Found:**
```json
{
  "success": false,
  "error": "Order not found or does not belong to buyer"
}
```

---

### 2. Get My Disputes (List)

Get a paginated list of all disputes created by the authenticated buyer.

**Endpoint:** `GET /api/products/user/disputes/`

**Request Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional, integer, default: 1) - Page number for pagination
- `limit` (optional, integer, default: 20) - Number of items per page
- `status` (optional, string) - Filter by status: `open`, `resolved`, or `closed`

**Example Requests:**
```
GET /api/products/user/disputes/
GET /api/products/user/disputes/?page=1&limit=10
GET /api/products/user/disputes/?status=open
GET /api/products/user/disputes/?page=2&limit=20&status=resolved
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "disputes": [
    {
      "_id": "507f191e810c19729de860ea",
      "caseNumber": "DISP-2024-0123",
      "type": "product_quality",
      "buyerName": "John Doe",
      "sellerName": "Jane Smith",
      "orderId": "507f1f77bcf86cd799439011",
      "orderNumber": "ORD-2024-ABCD1234",
      "itemTitle": "Premium Wireless Headphones",
      "description": "The product I received is damaged...",
      "status": "open",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "updatedAt": "2024-01-15T10:30:00.000Z",
      "messageCount": 2
    },
    {
      "_id": "507f191e810c19729de860eb",
      "caseNumber": "DISP-2024-0124",
      "type": "delivery_issue",
      "buyerName": "John Doe",
      "sellerName": "Bob Johnson",
      "orderId": "507f1f77bcf86cd799439012",
      "orderNumber": "ORD-2024-EFGH5678",
      "itemTitle": "Smart Watch",
      "description": "Order was not delivered on time...",
      "status": "resolved",
      "createdAt": "2024-01-10T08:15:00.000Z",
      "updatedAt": "2024-01-12T14:20:00.000Z",
      "messageCount": 5
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalItems": 25
  }
}
```

**Response Fields:**
- `_id` - Dispute MongoDB ObjectId
- `caseNumber` - Unique case number (e.g., "DISP-2024-0123")
- `type` - Dispute type
- `buyerName` - Buyer's name
- `sellerName` - Seller's name
- `orderId` - Order MongoDB ObjectId
- `orderNumber` - Human-readable order number (e.g., "ORD-2024-ABCD1234")
- `itemTitle` - Product title
- `description` - Dispute description
- `status` - Current status
- `createdAt` - Creation timestamp (ISO 8601)
- `updatedAt` - Last update timestamp (ISO 8601)
- `messageCount` - Number of messages/comments in the dispute

---

### 3. Get My Dispute Details

Get detailed information about a specific dispute. Buyers can only view their own disputes.

**Endpoint:** `GET /api/products/user/disputes/{dispute_id}/`

**Request Headers:**
```
Authorization: Bearer <token>
```

**URL Parameters:**
- `dispute_id` (required, string) - The MongoDB ObjectId of the dispute

**Example Request:**
```
GET /api/products/user/disputes/507f191e810c19729de860ea/
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "dispute": {
    "id": "507f191e810c19729de860ea",
    "caseNumber": "DISP-2024-0123",
    "type": "product_quality",
    "buyer": {
      "id": "507f1f77bcf86cd799439013",
      "name": "John Doe",
      "email": "john.doe@example.com"
    },
    "seller": {
      "id": "507f1f77bcf86cd799439014",
      "name": "Jane Smith",
      "email": "jane.smith@example.com"
    },
    "order": {
      "id": "507f1f77bcf86cd799439011",
      "orderNumber": "ORD-2024-ABCD1234"
    },
    "item": {
      "id": "507f1f77bcf86cd799439015",
      "title": "Premium Wireless Headphones",
      "price": 299.99
    },
    "description": "The product I received is damaged and not as described. The packaging was torn and the item inside is broken.",
    "status": "open",
    "adminNotes": "",
    "resolution": "",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T11:45:00.000Z",
    "messages": [
      {
        "message": "The product I received is damaged and not as described.",
        "senderType": "buyer",
        "senderId": "507f1f77bcf86cd799439013",
        "senderName": "John Doe",
        "createdAt": "2024-01-15T10:30:00.000Z"
      },
      {
        "message": "Thank you for reporting this issue. We are looking into it and will get back to you soon.",
        "senderType": "admin",
        "senderId": "507f1f77bcf86cd799439016",
        "senderName": "Admin User",
        "createdAt": "2024-01-15T11:00:00.000Z"
      },
      {
        "message": "I have attached photos of the damaged product. Please review.",
        "senderType": "buyer",
        "senderId": "507f1f77bcf86cd799439013",
        "senderName": "John Doe",
        "createdAt": "2024-01-15T11:30:00.000Z"
      }
    ],
    "timeline": [
      {
        "action": "dispute_created",
        "date": "2024-01-15T10:30:00.000Z",
        "by": "buyer"
      },
      {
        "action": "dispute_updated",
        "date": "2024-01-15T11:45:00.000Z",
        "by": "admin"
      }
    ]
  }
}
```

**Response Fields:**
- `id` - Dispute ID
- `caseNumber` - Unique case number
- `type` - Dispute type
- `buyer` - Buyer information (id, name, email)
- `seller` - Seller information (id, name, email)
- `order` - Order information (id, orderNumber)
- `item` - Product information (id, title, price)
- `description` - Dispute description
- `status` - Current status
- `adminNotes` - Internal admin notes (usually empty for buyers)
- `resolution` - Resolution details (if resolved)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `messages` - Array of all messages/comments (chronologically sorted)
  - `message` - Message content
  - `senderType` - Either "buyer" or "admin"
  - `senderId` - Sender's user ID
  - `senderName` - Sender's name
  - `createdAt` - Message timestamp
- `timeline` - Array of dispute events

**Error Responses:**

**404 Not Found - Dispute Not Found:**
```json
{
  "success": false,
  "error": "Dispute not found"
}
```

**403 Forbidden - Unauthorized:**
```json
{
  "success": false,
  "error": "Unauthorized: You can only view your own disputes"
}
```

---

### 4. Add Dispute Comment

Add a comment/response to a dispute. Buyers can only comment on their own disputes.

**Endpoint:** `POST /api/products/user/disputes/{dispute_id}/comments/`

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**URL Parameters:**
- `dispute_id` (required, string) - The MongoDB ObjectId of the dispute

**Request Body:**
```json
{
  "message": "I have attached photos of the damaged product. Please review and let me know the next steps."
}
```

**Request Parameters:**
- `message` (required, string) - The comment message

**Example Request:**
```
POST /api/products/user/disputes/507f191e810c19729de860ea/comments/
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Comment added successfully",
  "comment": {
    "id": "temp_id",
    "message": "I have attached photos of the damaged product. Please review and let me know the next steps.",
    "senderType": "buyer",
    "senderId": "507f1f77bcf86cd799439013",
    "senderName": "John Doe",
    "createdAt": "2024-01-15T12:00:00.000Z"
  }
}
```

**Response Fields:**
- `id` - Comment ID (temporary ID for embedded documents)
- `message` - Comment message
- `senderType` - Always "buyer" for buyer comments
- `senderId` - Buyer's user ID
- `senderName` - Buyer's name
- `createdAt` - Comment timestamp

**Error Responses:**

**400 Bad Request - Missing Message:**
```json
{
  "success": false,
  "error": "Message is required"
}
```

**404 Not Found - Dispute Not Found:**
```json
{
  "success": false,
  "error": "Dispute not found"
}
```

**403 Forbidden - Unauthorized:**
```json
{
  "success": false,
  "error": "Unauthorized: You can only comment on your own disputes"
}
```

---

## Complete Workflow Example

Here's a complete example of how a buyer would use the dispute system:

### Step 1: Buyer Creates a Dispute

**Request:**
```bash
POST /api/products/user/disputes/create/
Authorization: Bearer <buyer_token>
Content-Type: application/json

{
  "orderId": "507f1f77bcf86cd799439011",
  "disputeType": "product_quality",
  "description": "The product I received is damaged and not as described."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dispute/report submitted successfully. Admin will review it.",
  "dispute": {
    "id": "507f191e810c19729de860ea",
    "caseNumber": "DISP-2024-0123",
    "type": "product_quality",
    "status": "open",
    "createdAt": "2024-01-15T10:30:00.000Z"
  }
}
```

### Step 2: Buyer Views Their Disputes

**Request:**
```bash
GET /api/products/user/disputes/
Authorization: Bearer <buyer_token>
```

**Response:** (See "Get My Disputes" section above)

### Step 3: Buyer Views Dispute Details

**Request:**
```bash
GET /api/products/user/disputes/507f191e810c19729de860ea/
Authorization: Bearer <buyer_token>
```

**Response:** (See "Get My Dispute Details" section above)

### Step 4: Admin Responds (Admin Side)

Admin adds a comment via admin endpoint. Buyer receives email notification.

### Step 5: Buyer Responds to Admin

**Request:**
```bash
POST /api/products/user/disputes/507f191e810c19729de860ea/comments/
Authorization: Bearer <buyer_token>
Content-Type: application/json

{
  "message": "Thank you for looking into this. I have attached photos as requested."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Comment added successfully",
  "comment": {
    "id": "temp_id",
    "message": "Thank you for looking into this. I have attached photos as requested.",
    "senderType": "buyer",
    "senderId": "507f1f77bcf86cd799439013",
    "senderName": "John Doe",
    "createdAt": "2024-01-15T14:00:00.000Z"
  }
}
```

### Step 6: Admin Resolves Dispute (Admin Side)

Admin updates dispute status to "resolved" or "closed". Buyer receives notification.

### Step 7: Buyer Views Updated Dispute

**Request:**
```bash
GET /api/products/user/disputes/507f191e810c19729de860ea/
Authorization: Bearer <buyer_token>
```

**Response:** Shows updated status and resolution details.

---

## Error Handling

### Common Error Codes

**400 Bad Request**
- Missing required fields
- Invalid dispute type
- Invalid data format

**401 Unauthorized**
- Missing or invalid authentication token
- Token expired

**403 Forbidden**
- Trying to access another buyer's dispute
- Insufficient permissions

**404 Not Found**
- Dispute not found
- Order not found
- Invalid dispute ID

**500 Internal Server Error**
- Server-side errors
- Database connection issues

### Error Response Format

All error responses follow this format:
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

---

## Important Notes

1. **Authentication Required**: All endpoints require a valid authentication token
2. **Buyer-Only Access**: Buyers can only view and comment on their own disputes
3. **Order Validation**: Disputes can only be created for orders that belong to the authenticated buyer
4. **Email Notifications**: Buyers receive email notifications when admins reply to their disputes
5. **Chronological Messages**: Messages are sorted by creation date (oldest first)
6. **Case Numbers**: Each dispute gets a unique case number (e.g., "DISP-2024-0123")
7. **Order Numbers**: Each order has a human-readable order number (e.g., "ORD-2024-ABCD1234")
8. **Status Updates**: Only admins can change dispute status
9. **Timestamps**: All timestamps are in ISO 8601 format (UTC)

---

## Integration Tips

1. **Store Case Numbers**: Store the `caseNumber` for easy reference
2. **Poll for Updates**: Periodically check dispute status if needed
3. **Handle Notifications**: Implement email notification handling
4. **Error Handling**: Always handle 400, 401, 403, 404, and 500 errors
5. **Pagination**: Use pagination for disputes list if there are many disputes
6. **Status Filtering**: Use status filter to show only active disputes

---

## Support

For issues or questions about the dispute API, contact the development team or refer to the main API documentation.

