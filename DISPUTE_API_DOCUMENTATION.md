# Dispute Management API Documentation

Complete documentation for all dispute-related endpoints, including buyer and admin actions.

## Table of Contents
1. [Buyer Endpoints](#buyer-endpoints)
2. [Admin Endpoints](#admin-endpoints)
3. [Data Models](#data-models)
4. [Error Responses](#error-responses)

---

## Buyer Endpoints

### 1. Create Dispute
**Endpoint:** `POST /api/products/user/disputes/create/`  
**Authentication:** Required (Buyer only)

Create a new dispute for an order.

**Request Body:**
```json
{
  "orderId": "order_id_here",
  "disputeType": "product_quality" | "delivery_issue" | "payment_dispute",
  "description": "Detailed description of the dispute"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Dispute/report submitted successfully. Admin will review it.",
  "dispute": {
    "id": "dispute_id",
    "caseNumber": "DISP-2024-0001",
    "type": "product_quality",
    "status": "open",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

---

### 2. Get My Disputes
**Endpoint:** `GET /api/products/user/disputes/`  
**Authentication:** Required (Buyer only)

Get list of disputes created by the authenticated buyer.

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `limit` (optional, default: 20) - Items per page
- `status` (optional) - Filter by status: `open`, `resolved`, `closed`

**Response (200 OK):**
```json
{
  "success": true,
  "disputes": [
    {
      "_id": "dispute_id",
      "caseNumber": "DISP-2024-0001",
      "type": "product_quality",
      "buyerName": "John Doe",
      "sellerName": "Jane Smith",
      "orderId": "order_id",
      "itemTitle": "Product Name",
      "description": "Dispute description",
      "status": "open",
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T10:30:00Z",
      "messageCount": 3
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 100
  }
}
```

---

### 3. Get My Dispute Details
**Endpoint:** `GET /api/products/user/disputes/{dispute_id}/`  
**Authentication:** Required (Buyer only)

Get detailed information about a specific dispute. Buyers can only view their own disputes.

**Response (200 OK):**
```json
{
  "success": true,
  "dispute": {
    "id": "dispute_id",
    "caseNumber": "DISP-2024-0001",
    "type": "product_quality",
    "buyer": {
      "id": "buyer_id",
      "name": "John Doe",
      "email": "buyer@example.com"
    },
    "seller": {
      "id": "seller_id",
      "name": "Jane Smith",
      "email": "seller@example.com"
    },
    "order": {
      "id": "order_id",
      "orderNumber": "ORD-2024-0001"
    },
    "item": {
      "id": "product_id",
      "title": "Product Name",
      "price": 99.99
    },
    "description": "Detailed dispute description",
    "status": "open",
    "adminNotes": "",
    "resolution": "",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "messages": [
      {
        "message": "Admin response here",
        "senderType": "admin",
        "senderId": "admin_id",
        "senderName": "Admin User",
        "createdAt": "2024-01-15T11:00:00Z"
      },
      {
        "message": "Buyer follow-up",
        "senderType": "buyer",
        "senderId": "buyer_id",
        "senderName": "John Doe",
        "createdAt": "2024-01-15T11:30:00Z"
      }
    ],
    "timeline": [
      {
        "action": "dispute_created",
        "date": "2024-01-15T10:30:00Z",
        "by": "buyer"
      },
      {
        "action": "dispute_updated",
        "date": "2024-01-15T11:00:00Z",
        "by": "admin"
      }
    ]
  }
}
```

---

### 4. Add Dispute Comment (Buyer)
**Endpoint:** `POST /api/products/user/disputes/{dispute_id}/comments/`  
**Authentication:** Required (Buyer only)

Add a comment to a dispute. Buyers can only comment on their own disputes.

**Request Body:**
```json
{
  "message": "My comment or response"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Comment added successfully",
  "comment": {
    "id": "comment_id",
    "message": "My comment or response",
    "senderType": "buyer",
    "senderId": "buyer_id",
    "senderName": "John Doe",
    "createdAt": "2024-01-15T12:00:00Z"
  }
}
```

---

## Admin Endpoints

### 1. Get All Disputes
**Endpoint:** `GET /api/admin/disputes/`  
**Authentication:** Required (Admin only)

Get list of all disputes in the system.

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `limit` (optional, default: 20) - Items per page
- `status` (optional) - Filter by status: `open`, `resolved`, `closed`

**Response (200 OK):**
```json
{
  "success": true,
  "disputes": [
    {
      "_id": "dispute_id",
      "caseNumber": "DISP-2024-0001",
      "type": "product_quality",
      "buyerId": "buyer_id",
      "buyerName": "John Doe",
      "sellerId": "seller_id",
      "SellerName": "Jane Smith",
      "orderId": "order_id",
      "itemId": "product_id",
      "itemTitle": "Product Name",
      "description": "Dispute description",
      "status": "open",
      "createdAt": "2024-01-15T10:30:00Z",
      "adminNotes": "",
      "resolution": ""
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 10,
    "totalItems": 200
  }
}
```

---

### 2. Get Dispute Details (Admin)
**Endpoint:** `GET /api/admin/disputes/{dispute_id}/`  
**Authentication:** Required (Admin only)

Get detailed information about a specific dispute. Includes all information visible to buyers plus admin-specific data.

**Response (200 OK):**
```json
{
  "success": true,
  "dispute": {
    "id": "dispute_id",
    "caseNumber": "DISP-2024-0001",
    "type": "product_quality",
    "buyer": {
      "id": "buyer_id",
      "name": "John Doe",
      "email": "buyer@example.com"
    },
    "seller": {
      "id": "seller_id",
      "name": "Jane Smith",
      "email": "seller@example.com"
    },
    "order": {
      "id": "order_id",
      "orderNumber": "ORD-2024-0001"
    },
    "item": {
      "id": "product_id",
      "title": "Product Name",
      "price": 99.99
    },
    "description": "Detailed dispute description",
    "status": "open",
    "adminNotes": "Internal admin notes",
    "resolution": "",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "messages": [
      {
        "message": "Admin response",
        "senderType": "admin",
        "senderId": "admin_id",
        "senderName": "Admin User",
        "createdAt": "2024-01-15T11:00:00Z"
      },
      {
        "message": "Buyer response",
        "senderType": "buyer",
        "senderId": "buyer_id",
        "senderName": "John Doe",
        "createdAt": "2024-01-15T11:30:00Z"
      }
    ],
    "timeline": [
      {
        "action": "dispute_created",
        "date": "2024-01-15T10:30:00Z",
        "by": "buyer"
      },
      {
        "action": "dispute_updated",
        "date": "2024-01-15T11:00:00Z",
        "by": "admin"
      }
    ]
  }
}
```

**Admin Detail Page Information:**
The admin detail page shows:
- **Buyer Name**: Full name of the buyer who created the dispute
- **Seller Name**: Full name of the seller involved
- **Item Title**: Title/name of the product in dispute
- **Order ID**: The order ID associated with the dispute

---

### 3. Update Dispute Status
**Endpoint:** `PUT /api/admin/disputes/{dispute_id}/update/`  
**Authentication:** Required (Admin only)

Update dispute status, admin notes, or resolution.

**Request Body:**
```json
{
  "status": "open" | "resolved" | "closed",
  "adminNotes": "Internal admin notes (optional)",
  "resolution": "Resolution details (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "dispute": {
    "id": "dispute_id",
    "status": "resolved",
    "adminNotes": "Internal admin notes",
    "resolution": "Issue resolved in favor of buyer"
  }
}
```

**Note:** When status is set to `resolved`, both buyer and seller receive notifications.

---

### 4. Close Dispute
**Endpoint:** `PUT /api/admin/disputes/{dispute_id}/close/`  
**Authentication:** Required (Admin only)

Close a dispute with a resolution.

**Request Body:**
```json
{
  "resolution": "Final resolution details"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Dispute closed"
}
```

---

### 5. Add Dispute Comment (Admin)
**Endpoint:** `POST /api/admin/disputes/{dispute_id}/comments/`  
**Authentication:** Required (Admin only)

Add a comment to a dispute. **The buyer will automatically receive an email notification** when an admin replies.

**Request Body:**
```json
{
  "message": "Admin response or comment"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Comment added successfully. Buyer will be notified via email.",
  "comment": {
    "id": "comment_id",
    "message": "Admin response or comment",
    "senderType": "admin",
    "senderId": "admin_id",
    "senderName": "Admin User",
    "createdAt": "2024-01-15T12:00:00Z"
  }
}
```

**Email Notification:**
When an admin adds a comment:
- Buyer receives an email notification
- Email subject: "New Reply on Dispute {case_number}"
- Email includes link to view the dispute
- Supports both English and Arabic based on buyer's language preference

---

### 6. Upload Dispute Evidence
**Endpoint:** `POST /api/admin/disputes/{dispute_id}/evidence/`  
**Authentication:** Required (Admin only)

Upload evidence files for a dispute (currently placeholder implementation).

**Request Body (multipart/form-data):**
- `file` (required) - Evidence file
- `description` (optional) - Description of the evidence

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Evidence uploaded successfully",
  "evidence": {
    "id": "evidence_id",
    "type": "image",
    "url": "/media/disputes/dispute_id/file.jpg",
    "description": "Evidence description",
    "uploaded_at": "2024-01-15T12:00:00Z",
    "uploaded_by": {
      "id": "admin_id",
      "name": "Admin User"
    }
  }
}
```

---

## Data Models

### Dispute Model
```python
{
  "case_number": "DISP-2024-0001",  # Unique case identifier
  "dispute_type": "product_quality" | "delivery_issue" | "payment_dispute",
  "buyer_id": "user_id",
  "buyer_name": "John Doe",
  "seller_id": "user_id",
  "seller_name": "Jane Smith",
  "order_id": "order_id",  # Required: Order associated with dispute
  "item_id": "product_id",
  "item_title": "Product Name",
  "description": "Dispute description",
  "status": "open" | "resolved" | "closed",
  "admin_notes": "Internal admin notes",
  "resolution": "Resolution details",
  "messages": [  # Array of comments
    {
      "message": "Comment text",
      "sender_type": "buyer" | "admin",
      "sender_id": "user_id",
      "sender_name": "Name",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Dispute Types
- `product_quality` - Issues with product quality or condition
- `delivery_issue` - Problems with delivery or shipping
- `payment_dispute` - Payment-related disputes

### Dispute Status
- `open` - Dispute is active and being reviewed
- `resolved` - Dispute has been resolved
- `closed` - Dispute is closed (final state)

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Order ID is required"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Dispute not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error message"
}
```

---

## Workflow Example

1. **Buyer creates dispute:**
   ```
   POST /api/products/user/disputes/create/
   → Dispute created with status "open"
   ```

2. **Buyer views their disputes:**
   ```
   GET /api/products/user/disputes/
   → List of buyer's disputes
   ```

3. **Admin views dispute:**
   ```
   GET /api/admin/disputes/{dispute_id}/
   → Full dispute details
   ```

4. **Admin adds comment:**
   ```
   POST /api/admin/disputes/{dispute_id}/comments/
   → Comment added, buyer receives email notification
   ```

5. **Buyer responds:**
   ```
   POST /api/products/user/disputes/{dispute_id}/comments/
   → Buyer's comment added
   ```

6. **Admin resolves dispute:**
   ```
   PUT /api/admin/disputes/{dispute_id}/update/
   → Status changed to "resolved", notifications sent
   ```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Buyers can only view and comment on their own disputes
- Admins have full access to all disputes
- Email notifications are sent automatically when admins reply
- Disputes are indexed by `buyer_id` and `order_id` for efficient queries
- Comments are stored in chronological order within the dispute

