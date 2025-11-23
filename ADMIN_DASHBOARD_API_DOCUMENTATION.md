# Dolabb Admin Dashboard API Documentation

## Base URL
```
https://dolabb-backend-2vsj.onrender.com
```

## Authentication
All endpoints require Admin JWT token in the Authorization header:
```
Authorization: Bearer <admin_jwt_token>
```

**Important:** Only users with `role: "admin"` can access these endpoints.

---

## Table of Contents
1. [Admin Authentication](#admin-authentication-endpoints)
2. [Dashboard Statistics](#dashboard-statistics-endpoints)
3. [User Management](#user-management-endpoints)
4. [Listing Management](#listing-management-endpoints)
5. [Transactions](#transactions-endpoints)
6. [Cashout Requests](#cashout-requests-endpoints)
7. [Fee Settings](#fee-settings-endpoints)
8. [Disputes](#disputes-endpoints)
9. [Affiliate Management](#affiliate-management-endpoints)
10. [Notification Management](#notification-management-endpoints)
11. [State Management](#state-management-recommendations)
12. [Toast Messages](#toast-messages)

---

## Admin Authentication Endpoints

### 1. Admin Signup
**Endpoint:** `POST /api/auth/admin/signup/`

**Request Body:**
```json
{
  "name": "Admin User",
  "email": "admin@dolabb.com",
  "password": "admin123",
  "confirm_password": "admin123",
  "profile_image_url": "https://example.com/image.jpg"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Admin registered successfully. OTP sent to email. Please verify OTP to complete registration.",
  "otp": "1234",
  "admin": {
    "id": "admin_id",
    "name": "Admin User",
    "email": "admin@dolabb.com",
    "role": "admin"
  }
}
```

**Toast Message:** `"Admin registration successful! Please check your email for OTP verification."`

---

### 2. Admin Login
**Endpoint:** `POST /api/auth/admin/login/`

**Request Body:**
```json
{
  "email": "admin@dolabb.com",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "admin": {
    "id": "admin_id",
    "name": "Admin User",
    "email": "admin@dolabb.com",
    "role": "admin"
  },
  "token": "jwt_token_here"
}
```

**Toast Message:** `"Welcome back, {name}!"`

---

### 3. Admin Verify OTP
**Endpoint:** `POST /api/auth/admin/verify-otp/`

**Request Body:**
```json
{
  "email": "admin@dolabb.com",
  "otp": "1234"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "admin": {
    "id": "admin_id",
    "name": "Admin User",
    "email": "admin@dolabb.com",
    "role": "admin",
    "profile_image": "https://example.com/image.jpg"
  },
  "token": "jwt_token_here"
}
```

**Toast Message:** `"Email verified successfully! Your admin account is now active."`

---

### 4. Admin Forgot Password
**Endpoint:** `POST /api/auth/admin/forgot-password/`

**Request Body:**
```json
{
  "email": "admin@dolabb.com"
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

### 5. Admin Reset Password
**Endpoint:** `POST /api/auth/admin/reset-password/`

**Request Body:**
```json
{
  "email": "admin@dolabb.com",
  "otp": "1234",
  "new_password": "newadmin123",
  "confirm_password": "newadmin123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

**Toast Message:** `"Password reset successfully! Please login with your new password."`

---

## Dashboard Statistics Endpoints

### 6. Get Dashboard Stats
**Endpoint:** `GET /api/admin/dashboard/stats/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "totalUsers": 1500,
  "activeUsers": 1200,
  "totalListings": 5000,
  "Total Sales": 2500,
  "totalTransactions": 3000,
  "totalRevenue": 150000.00,
  "pendingCashouts": 15,
  "recentActivities": [
    {
      "type": "new_order",
      "details": "New order #ORD123456",
      "date": "2024-01-01T00:00:00Z"
    }
  ],
  "Open Disputes": 5,
  "resolvedDisputes": 50
}
```

---

### 7. Get Revenue Trends
**Endpoint:** `GET /api/admin/dashboard/revenue-trends/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "monthlyRevenue": [
    {
      "month": "2024-01",
      "revenue": 50000.00
    },
    {
      "month": "2024-02",
      "revenue": 60000.00
    }
  ],
  "totalRevenue": 150000.00,
  "growthRate": 20.5
}
```

---

### 8. Get Sales Over Time
**Endpoint:** `GET /api/admin/dashboard/sales-over-time/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `period` (optional): `"daily"`, `"weekly"`, `"monthly"` (default: `"monthly"`)
- `fromDate` (optional): Start date (ISO format)
- `toDate` (optional): End date (ISO format)

**Response (200 OK):**
```json
{
  "success": true,
  "sales": [
    {
      "date": "2024-01-01",
      "count": 50,
      "revenue": 5000.00
    },
    {
      "date": "2024-01-02",
      "count": 60,
      "revenue": 6000.00
    }
  ],
  "totalSales": 2500,
  "totalRevenue": 150000.00
}
```

---

### 9. Get Listings Status Summary
**Endpoint:** `GET /api/admin/dashboard/listings-status/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "pending": 100,
  "approved": 4500,
  "rejected": 200,
  "hidden": 200,
  "total": 5000
}
```

---

### 10. Get Transaction Types Summary
**Endpoint:** `GET /api/admin/dashboard/transaction-types/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "purchases": 2000,
  "sales": 2500,
  "refunds": 50,
  "fees": 3000,
  "total": 7550
}
```

---

### 10. Get Disputes Status
**Endpoint:** `GET /api/admin/dashboard/disputes-status/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "open": 5,
  "inProgress": 10,
  "resolved": 50,
  "closed": 100,
  "total": 165
}
```

---

### 11. Get Cashout Requests Summary
**Endpoint:** `GET /api/admin/dashboard/cashout-requests-summary/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "pending": 15,
  "approved": 100,
  "rejected": 10,
  "total": 125,
  "totalAmount": {
    "pending": 5000.00,
    "approved": 50000.00,
    "rejected": 2000.00
  }
}
```

---

## User Management Endpoints

### 12. Get Users
**Endpoint:** `GET /api/admin/users/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`active`, `suspended`, `deactivated`)

**Response (200 OK):**
```json
{
  "success": true,
  "users": [
    {
      "id": "user_id",
      "username": "johndoe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "full_name": "John Doe",
      "role": "buyer",
      "status": "active",
      "join_date": "2024-01-01T00:00:00Z",
      "total_orders": 10,
      "total_spent": 1000.00
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 75,
    "totalItems": 1500
  }
}
```

---

### 13. Suspend User
**Endpoint:** `PUT /api/admin/users/{user_id}/suspend/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User suspended"
}
```

**Toast Message:** `"User suspended successfully!"`

---

### 14. Deactivate User
**Endpoint:** `PUT /api/admin/users/{user_id}/deactivate/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deactivated"
}
```

**Toast Message:** `"User deactivated successfully!"`

---

### 15. Delete User
**Endpoint:** `DELETE /api/admin/users/{user_id}/delete/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted"
}
```

**Toast Message:** `"User deleted successfully!"`

---

## Listing Management Endpoints

### 16. Get Listings
**Endpoint:** `GET /api/admin/listings/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`, `hidden`)

**Response (200 OK):**
```json
{
  "success": true,
  "listings": [
    {
      "id": "product_id",
      "title": "Product Title",
      "description": "Product description",
      "price": 99.99,
      "category": "Electronics",
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "email": "seller@example.com"
      },
      "status": "pending",
      "approved": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 250,
    "totalItems": 5000
  }
}
```

---

### 17. Approve Listing
**Endpoint:** `PUT /api/admin/listings/{listing_id}/approve/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing approved"
}
```

**Toast Message:** `"Listing approved successfully!"`

---

### 18. Reject Listing
**Endpoint:** `PUT /api/admin/listings/{listing_id}/reject/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing rejected"
}
```

**Toast Message:** `"Listing rejected!"`

---

### 19. Hide Listing
**Endpoint:** `PUT /api/admin/listings/{listing_id}/hide/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing hidden"
}
```

**Toast Message:** `"Listing hidden successfully!"`

---

## Transactions Endpoints

### 20. Get Transactions
**Endpoint:** `GET /api/admin/transactions/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `type` (optional): Filter by type (`purchase`, `sale`, `refund`, `fee`)

**Response (200 OK):**
```json
{
  "success": true,
  "transactions": [
    {
      "id": "transaction_id",
      "type": "purchase",
      "amount": 109.99,
      "currency": "SAR",
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "email": "buyer@example.com"
      },
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "email": "seller@example.com"
      },
      "order": {
        "id": "order_id",
        "orderNumber": "ORD123456"
      },
      "platformFee": 5.50,
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 150,
    "totalItems": 3000
  }
}
```

---

## Cashout Requests Endpoints

### 21. Get Cashout Requests
**Endpoint:** `GET /api/admin/cashout-requests/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`)

**Response (200 OK):**
```json
{
  "success": true,
  "cashoutRequests": [
    {
      "id": "cashout_id",
      "affiliateId": "affiliate_id",
      "affiliateName": "Affiliate Name",
      "amount": 500.00,
      "paymentMethod": "Bank Transfer",
      "accountDetails": "123456789",
      "status": "pending",
      "requestedAt": "2024-01-01T00:00:00Z",
      "processedAt": null,
      "processedBy": null
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 8,
    "totalItems": 125
  }
}
```

---

### 22. Approve Cashout
**Endpoint:** `PUT /api/admin/cashout-requests/{cashout_id}/approve/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Cashout approved"
}
```

**Toast Message:** `"Cashout request approved successfully!"`

---

### 23. Reject Cashout
**Endpoint:** `PUT /api/admin/cashout-requests/{cashout_id}/reject/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "reason": "Insufficient documentation"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Cashout rejected"
}
```

**Toast Message:** `"Cashout request rejected!"`

---

## Fee Settings Endpoints

### 24. Get Fee Settings
**Endpoint:** `GET /api/admin/fee-settings/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "minimumFee": 2.00,
  "feePercentage": 5.5,
  "thresholdAmount1": 100.00,
  "thresholdAmount2": 500.00,
  "maximumFee": 50.00,
  "transactionFeeFixed": 2.00,
  "defaultAffiliateCommissionPercentage": 10.0,
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

---

### 25. Update Fee Settings
**Endpoint:** `PUT /api/admin/fee-settings/update/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "minimumFee": 2.00,
  "feePercentage": 5.5,
  "thresholdAmount1": 100.00,
  "thresholdAmount2": 500.00,
  "maximumFee": 50.00,
  "transactionFeeFixed": 2.00,
  "defaultAffiliateCommissionPercentage": 10.0
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "minimumFee": 2.00,
  "feePercentage": 5.5,
  "thresholdAmount1": 100.00,
  "thresholdAmount2": 500.00,
  "maximumFee": 50.00,
  "transactionFeeFixed": 2.00,
  "defaultAffiliateCommissionPercentage": 10.0,
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

**Toast Message:** `"Fee settings updated successfully!"`

---

### 26. Get Fee Collection Summary
**Endpoint:** `GET /api/admin/fee-settings/summary/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `fromDate` (optional): Start date (ISO format)
- `toDate` (optional): End date (ISO format)

**Response (200 OK):**
```json
{
  "success": true,
  "totalFees": 15000.00,
  "totalTransactions": 3000,
  "averageFee": 5.00,
  "feesByPeriod": [
    {
      "period": "2024-01",
      "fees": 5000.00,
      "transactions": 1000
    }
  ]
}
```

---

## Disputes Endpoints

### 27. Get Disputes
**Endpoint:** `GET /api/admin/disputes/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`open`, `in_progress`, `resolved`, `closed`)

**Response (200 OK):**
```json
{
  "success": true,
  "disputes": [
    {
      "id": "dispute_id",
      "orderId": "order_id",
      "orderNumber": "ORD123456",
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "email": "buyer@example.com"
      },
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "email": "seller@example.com"
      },
      "reason": "Item not as described",
      "description": "The item received does not match the description",
      "status": "open",
      "adminNotes": "",
      "resolution": "",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 17,
    "totalItems": 165
  }
}
```

---

### 28. Update Dispute
**Endpoint:** `PUT /api/admin/disputes/{dispute_id}/update/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "status": "in_progress",
  "adminNotes": "Investigating the issue",
  "resolution": ""
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "dispute": {
    "id": "dispute_id",
    "status": "in_progress",
    "adminNotes": "Investigating the issue",
    "resolution": ""
  }
}
```

**Toast Message:** `"Dispute updated successfully!"`

---

### 29. Close Dispute
**Endpoint:** `PUT /api/admin/disputes/{dispute_id}/close/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "resolution": "Refund issued to buyer"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Dispute closed"
}
```

**Toast Message:** `"Dispute closed successfully!"`

---

## Affiliate Management Endpoints

### 30. Get All Affiliates
**Endpoint:** `GET /api/affiliate/all/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "affiliates": [
    {
      "id": "affiliate_id",
      "full_name": "Affiliate Name",
      "email": "affiliate@example.com",
      "phone": "+1234567890",
      "affiliate_code": "AFF123",
      "totalEarnings": 1000.00,
      "pendingEarnings": 500.00,
      "paidEarnings": 500.00,
      "codeUsageCount": 50,
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
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

### 31. Get Affiliate Transactions
**Endpoint:** `GET /api/affiliate/{affiliate_id}/transactions/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "transactions": [
    {
      "id": "transaction_id",
      "orderId": "order_id",
      "orderNumber": "ORD123456",
      "commission": 10.00,
      "commissionRate": 10.0,
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z"
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

### 32. Update Commission Rate
**Endpoint:** `PUT /api/affiliate/{affiliate_id}/update-commission/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "commissionRate": 15.0
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Commission rate updated",
  "affiliate": {
    "id": "affiliate_id",
    "commissionRate": 15.0
  }
}
```

**Toast Message:** `"Commission rate updated successfully!"`

---

### 33. Suspend Affiliate
**Endpoint:** `PUT /api/affiliate/{affiliate_id}/suspend/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Affiliate suspended"
}
```

**Toast Message:** `"Affiliate suspended successfully!"`

---

### 34. Get Payout Requests
**Endpoint:** `GET /api/affiliate/payout-requests/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`)

**Response (200 OK):**
```json
{
  "success": true,
  "payoutRequests": [
    {
      "id": "payout_id",
      "affiliateId": "affiliate_id",
      "affiliateName": "Affiliate Name",
      "amount": 500.00,
      "paymentMethod": "Bank Transfer",
      "accountDetails": "123456789",
      "status": "pending",
      "requestedAt": "2024-01-01T00:00:00Z",
      "processedAt": null,
      "processedBy": null
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 8,
    "totalItems": 125
  }
}
```

---

### 35. Approve Payout
**Endpoint:** `PUT /api/affiliate/payout-requests/{payout_id}/approve/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Payout approved"
}
```

**Toast Message:** `"Payout request approved successfully!"`

---

### 36. Reject Payout
**Endpoint:** `PUT /api/affiliate/payout-requests/{payout_id}/reject/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "reason": "Insufficient documentation"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Payout rejected"
}
```

**Toast Message:** `"Payout request rejected!"`

---

## Notification Management Endpoints

### 37. Create Notification
**Endpoint:** `POST /api/notifications/admin/create/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "title": "New Feature Available",
  "message": "Check out our new feature!",
  "type": "announcement",
  "targetAudience": "all",
  "scheduledFor": "2024-01-01T12:00:00Z",
  "variables": {}
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "notification": {
    "id": "notification_id",
    "title": "New Feature Available",
    "message": "Check out our new feature!",
    "type": "announcement",
    "targetAudience": "all"
  }
}
```

**Toast Message:** `"Notification created successfully!"`

---

### 38. Send Notification
**Endpoint:** `POST /api/notifications/admin/{notification_id}/send/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification sent to 1500 users"
}
```

**Toast Message:** `"Notification sent to {count} users!"`

---

### 39. Get Admin Notifications
**Endpoint:** `GET /api/notifications/admin/list/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `search` (optional): Search query
- `type` (optional): Filter by type
- `dateFrom` (optional): Start date (ISO format)
- `dateTo` (optional): End date (ISO format)

**Response (200 OK):**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "notification_id",
      "title": "New Feature Available",
      "message": "Check out our new feature!",
      "type": "announcement",
      "targetAudience": "all",
      "active": true,
      "sentCount": 1500,
      "createdAt": "2024-01-01T00:00:00Z",
      "scheduledFor": "2024-01-01T12:00:00Z"
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

### 40. Update Notification
**Endpoint:** `PUT /api/notifications/admin/{notification_id}/update/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "message": "Updated message",
  "active": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "notification": {
    "id": "notification_id",
    "title": "Updated Title",
    "message": "Updated message",
    "active": true
  }
}
```

**Toast Message:** `"Notification updated successfully!"`

---

### 41. Delete Admin Notification
**Endpoint:** `DELETE /api/notifications/admin/{notification_id}/delete/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification deleted"
}
```

**Toast Message:** `"Notification deleted successfully!"`

---

## State Management Recommendations

### Recommended Approach: Redux Toolkit + RTK Query

For the Admin Dashboard, we recommend using **Redux Toolkit** with **RTK Query** for the following reasons:

1. **Complex State Management**: 
   - Dashboard statistics and metrics
   - User management with filters and pagination
   - Listing management with bulk operations
   - Transaction tracking
   - Real-time updates for disputes and cashouts

2. **RTK Query Benefits**:
   - Automatic caching and invalidation
   - Request deduplication
   - Background refetching
   - Optimistic updates
   - Built-in loading/error states

### State Structure Example:

```typescript
// Admin Dashboard Store structure
{
  auth: {
    admin: Admin | null,
    token: string | null,
    isAuthenticated: boolean,
    loading: boolean
  },
  dashboard: {
    stats: DashboardStats | null,
    revenueTrends: RevenueTrend[],
    salesOverTime: SalesData[],
    listingsStatus: ListingsStatus | null,
    transactionTypes: TransactionTypes | null,
    disputesStatus: DisputesStatus | null,
    cashoutSummary: CashoutSummary | null
  },
  users: {
    items: User[],
    filters: UserFilters,
    pagination: PaginationState,
    selectedUser: User | null
  },
  listings: {
    items: Listing[],
    filters: ListingFilters,
    pagination: PaginationState,
    selectedListing: Listing | null
  },
  transactions: {
    items: Transaction[],
    filters: TransactionFilters,
    pagination: PaginationState
  },
  cashouts: {
    items: CashoutRequest[],
    filters: CashoutFilters,
    pagination: PaginationState
  },
  disputes: {
    items: Dispute[],
    filters: DisputeFilters,
    pagination: PaginationState,
    selectedDispute: Dispute | null
  },
  feeSettings: {
    settings: FeeSettings | null,
    summary: FeeCollectionSummary | null
  },
  affiliates: {
    items: Affiliate[],
    pagination: PaginationState,
    selectedAffiliate: Affiliate | null,
    transactions: AffiliateTransaction[]
  },
  notifications: {
    items: AdminNotification[],
    pagination: PaginationState,
    selectedNotification: AdminNotification | null
  }
}
```

### API Client Setup (Axios Example):

```typescript
import axios from 'axios';

const adminApiClient = axios.create({
  baseURL: 'https://dolabb-backend-2vsj.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add admin token to requests
adminApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration and unauthorized access
adminApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to admin login
      localStorage.removeItem('admin_token');
      window.location.href = '/admin/login';
    } else if (error.response?.status === 403) {
      // Not an admin user
      toast.error('Access denied. Admin privileges required.');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);
```

### Real-time Updates

For real-time updates in the admin dashboard, consider:

1. **WebSocket Connection**: Connect to notification WebSocket for real-time updates
2. **Polling**: Use RTK Query's polling feature for dashboard stats
3. **Optimistic Updates**: Update UI immediately for better UX

```typescript
// Example: Polling dashboard stats every 30 seconds
const { data, error, isLoading } = useGetDashboardStatsQuery(undefined, {
  pollingInterval: 30000, // Poll every 30 seconds
});
```

---

## Toast Messages

### Success Messages

| Action | Message |
|--------|---------|
| Admin Signup | "Admin registration successful! Please check your email for OTP verification." |
| Admin Login | "Welcome back, {name}!" |
| OTP Verified | "Email verified successfully! Your admin account is now active." |
| Password Reset | "Password reset successfully! Please login with your new password." |
| User Suspended | "User suspended successfully!" |
| User Deactivated | "User deactivated successfully!" |
| User Deleted | "User deleted successfully!" |
| Listing Approved | "Listing approved successfully!" |
| Listing Rejected | "Listing rejected!" |
| Listing Hidden | "Listing hidden successfully!" |
| Cashout Approved | "Cashout request approved successfully!" |
| Cashout Rejected | "Cashout request rejected!" |
| Fee Settings Updated | "Fee settings updated successfully!" |
| Dispute Updated | "Dispute updated successfully!" |
| Dispute Closed | "Dispute closed successfully!" |
| Commission Rate Updated | "Commission rate updated successfully!" |
| Affiliate Suspended | "Affiliate suspended successfully!" |
| Payout Approved | "Payout request approved successfully!" |
| Payout Rejected | "Payout request rejected!" |
| Notification Created | "Notification created successfully!" |
| Notification Sent | "Notification sent to {count} users!" |
| Notification Updated | "Notification updated successfully!" |
| Notification Deleted | "Notification deleted successfully!" |

### Error Messages

| Error Type | Message |
|-----------|---------|
| Invalid Credentials | "Invalid email or password. Please try again." |
| OTP Expired | "OTP has expired. Please request a new one." |
| Invalid OTP | "Invalid OTP. Please check and try again." |
| Unauthorized | "Session expired. Please login again." |
| Forbidden | "Access denied. Admin privileges required." |
| User Not Found | "User not found." |
| Listing Not Found | "Listing not found." |
| Transaction Not Found | "Transaction not found." |
| Network Error | "Network error. Please check your connection and try again." |
| Server Error | "Server error. Please try again later." |

### Warning Messages

| Action | Message |
|--------|---------|
| Delete User | "Are you sure you want to delete this user? This action cannot be undone." |
| Reject Listing | "Are you sure you want to reject this listing?" |
| Reject Cashout | "Are you sure you want to reject this cashout request?" |
| Suspend User | "Are you sure you want to suspend this user?" |

### Info Messages

| Action | Message |
|--------|---------|
| Loading | "Loading..." |
| Processing | "Processing..." |
| Saving | "Saving changes..." |
| Fetching Data | "Fetching data..." |

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
- `403 Forbidden`: Insufficient permissions (not an admin)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Handling Example:

```typescript
try {
  const response = await adminApiClient.put(`/api/admin/users/${userId}/suspend`);
  if (response.data.success) {
    toast.success('User suspended successfully!');
    // Refresh users list
    dispatch(refetchUsers());
  }
} catch (error) {
  if (error.response?.status === 401) {
    toast.error('Session expired. Please login again.');
    // Redirect to login
  } else if (error.response?.status === 403) {
    toast.error('Access denied. Admin privileges required.');
  } else if (error.response?.status === 404) {
    toast.error('User not found.');
  } else {
    toast.error(error.response?.data?.error || 'An error occurred');
  }
}
```

---

## Best Practices

1. **Token Management**: 
   - Store admin token securely (consider httpOnly cookies for production)
   - Implement token refresh logic
   - Clear token on logout

2. **Error Handling**:
   - Always check `success` field in responses
   - Handle network errors gracefully
   - Show user-friendly error messages

3. **Loading States**:
   - Show loading indicators during API calls
   - Use skeleton loaders for better UX

4. **Pagination**:
   - Implement infinite scroll or pagination controls
   - Cache paginated data appropriately

5. **Real-time Updates**:
   - Use WebSocket for real-time notifications
   - Poll critical data (dashboard stats) at appropriate intervals

6. **Optimistic Updates**:
   - Update UI immediately for better UX
   - Rollback on error

7. **Data Validation**:
   - Validate data on frontend before sending
   - Handle validation errors from backend

8. **Security**:
   - Never expose admin tokens in client-side code
   - Implement proper CORS policies
   - Validate all user inputs

---

## Support

For API support or questions, contact the development team.

**Base URL:** `https://dolabb-backend-2vsj.onrender.com`

**Admin Panel URL:** `https://dolabb-backend-2vsj.onrender.com/admin/`

