# Affiliate API Documentation

## Base URL
```
https://dolabb-backend-2vsj.onrender.com/api/affiliate/
```

## Authentication
Most endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

Admin endpoints require admin privileges.

---

## Quick Reference: Affiliate Dashboard Data

**For the affiliate dashboard, use these endpoints:**

### Summary Data (Total Earnings, Pending, Available Balance, Status)
**Endpoint:** `GET /api/affiliate/profile/`

This endpoint returns:
- ✅ **Total Earnings** (`totalEarnings`)
- ✅ **Pending Earnings** (`pendingEarnings`)
- ✅ **Available Balance** (`availableBalance` - same as pendingEarnings)
- ✅ **Paid Earnings** (`paidEarnings`)
- ✅ **Status** (`status` - "active" or "deactivated")
- ✅ **Commission Rate** (`commission_rate`)
- ✅ **Code Usage Count** (`codeUsageCount`)

### Earning Breakdown (Detailed Transaction List)
**Endpoint:** `GET /api/affiliate/transactions/`

This endpoint returns:
- ✅ **Earning Breakdown** - List of all transactions with:
  - Transaction ID
  - Referred User Name
  - Commission Amount
  - Date
  - Status (pending/paid)
  - Overall stats (totalReferrals, totalEarnings, Total Sales, Commission Rate)

**Example Dashboard Implementation:**
```javascript
// Get summary data
const profile = await axios.get('/api/affiliate/profile/', {
  headers: { Authorization: `Bearer ${token}` }
});

// Get earning breakdown
const transactions = await axios.get('/api/affiliate/transactions/?page=1&limit=20', {
  headers: { Authorization: `Bearer ${token}` }
});
```

---

## Public Endpoints

### 1. Validate Affiliate Code
Validate if an affiliate code is valid and active.

**Endpoint:** `POST /api/affiliate/validate-code/`

**Authentication:** Not required (public)

**Request Body:**
```json
{
  "code": "AFFILIATE123"
}
```

**Success Response (200):**
```json
{
  "valid": true,
  "message": "Valid affiliate code",
  "affiliate": {
    "id": "507f1f77bcf86cd799439011",
    "fullName": "John Doe",
    "email": "john@example.com",
    "affiliateCode": "AFFILIATE123",
    "commissionRate": "25.0",
    "status": "active"
  }
}
```

**Error Response (200):**
```json
{
  "valid": false,
  "message": "Invalid or inactive affiliate code"
}
```

---

## Affiliate Endpoints (Authenticated)

### 2. Get Affiliate Profile
Get the authenticated affiliate's profile information.

**Endpoint:** `GET /api/affiliate/profile/`

**Authentication:** Required (Affiliate)

**Success Response (200):**
```json
{
  "success": true,
  "affiliate": {
    "id": "507f1f77bcf86cd799439011",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "country_code": "+1",
    "affiliate_code": "AFFILIATE123",
    "profile_image": "https://example.com/media/profile.jpg",
    "totalEarnings": 1500.50,
    "totalCommissions": 1500.50,
    "pendingEarnings": 500.25,
    "paidEarnings": 1000.25,
    "codeUsageCount": 15,
    "availableBalance": 500.25,
    "commission_rate": 25.0,
    "status": "active",
    "bank_details": {
      "bank_name": "Bank Name",
      "account_number": "123456789",
      "iban": "SA1234567890123456789012",
      "account_holder_name": "John Doe"
    },
    "created_at": "2024-01-01T00:00:00.000Z",
    "last_activity": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Unauthorized. Affiliate access required."
}
```

---

### 3. Get My Transactions (Earning Breakdown)
Get the authenticated affiliate's transaction history with earning breakdown.

**Endpoint:** `GET /api/affiliate/transactions/`

**Authentication:** Required (Affiliate)

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Example:** `GET /api/affiliate/transactions/?page=1&limit=20`

**Success Response (200):**
```json
{
  "success": true,
  "transactions": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "affiliateId": "507f1f77bcf86cd799439011",
      "affiliateName": "John Doe",
      "stats": {
        "totalReferrals": 15,
        "totalEarnings": 1500.50,
        "Total Sales": 15,
        "Commission Rate": 25.0
      },
      "Transaction ID": "507f1f77bcf86cd799439014",
      "date": "2024-01-15T10:30:00.000Z",
      "Referred User Name": "Jane Smith",
      "Referred User Commission": 100.25,
      "status": "paid"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalItems": 50
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Unauthorized. Affiliate access required."
}
```

---

### 4. Update Affiliate Profile
Update the authenticated affiliate's profile information.

**Endpoint:** `PUT /api/affiliate/profile/`

**Authentication:** Required (Affiliate)

**Request Body:**
```json
{
  "full_name": "John Doe Updated",
  "phone": "+1234567890",
  "country_code": "+1",
  "profile_image": "data:image/jpeg;base64,...",
  "bank_name": "New Bank Name",
  "account_number": "987654321",
  "iban": "SA9876543210987654321098",
  "account_holder_name": "John Doe"
}
```

**Note:** All fields are optional. Only include fields you want to update.

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "affiliate": {
    // Same structure as GET profile response
  }
}
```

---

### 5. Request Cashout
Request a payout from pending earnings.

**Endpoint:** `POST /api/affiliate/cashout/`

**Authentication:** Required (Affiliate)

**Request Body:**
```json
{
  "amount": 500.00,
  "paymentMethod": "Bank Transfer"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "cashoutRequest": {
    "id": "507f1f77bcf86cd799439012",
    "affiliateId": "507f1f77bcf86cd799439011",
    "amount": 500.00,
    "status": "pending",
    "requestedAt": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Insufficient pending earnings"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Affiliate not found"
}
```

---

## Admin Endpoints

### 6. Get All Affiliates
Get a paginated list of all affiliates (admin only).

**Endpoint:** `GET /api/affiliate/all/`

**Authentication:** Required (Admin)

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Example:** `GET /api/affiliate/all/?page=1&limit=20`

**Success Response (200):**
```json
{
  "success": true,
  "affiliates": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "Affiliatename": "John Doe",
      "Affiliateemail": "john@example.com",
      "affiliateCode": "AFFILIATE123",
      "commissionRate": 25.0,
      "codeUsageCount": 15,
      "Earnings": {
        "Total": 1500.50,
        "Pending": 500.25,
        "Paid": 1000.25
      },
      "Affiliatestatus": "active",
      "Last Activity": "2024-01-15T10:30:00.000Z",
      "stats": {
        "totalReferrals": 15,
        "totalEarnings": 1500.50,
        "totalTransactions": 15
      }
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 100
  }
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 7. Get Affiliate Transactions (Admin)
Get transaction history for a specific affiliate (admin only).

**Endpoint:** `GET /api/affiliate/{affiliate_id}/transactions/`

**Authentication:** Required (Admin)

**URL Parameters:**
- `affiliate_id`: The affiliate's ID

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Example:** `GET /api/affiliate/507f1f77bcf86cd799439011/transactions/?page=1&limit=20`

**Success Response (200):**
```json
{
  "success": true,
  "transactions": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "affiliateId": "507f1f77bcf86cd799439011",
      "affiliateName": "John Doe",
      "stats": {
        "totalReferrals": 15,
        "totalEarnings": 1500.50,
        "Total Sales": 15,
        "Commission Rate": 25.0
      },
      "Transaction ID": "507f1f77bcf86cd799439014",
      "date": "2024-01-15T10:30:00.000Z",
      "Referred User Name": "Jane Smith",
      "Referred User Commission": 100.25,
      "status": "paid"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalItems": 50
  }
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 8. Update Commission Rate
Update an affiliate's commission rate (admin only).

**Endpoint:** `PUT /api/affiliate/{affiliate_id}/update-commission/`

**Authentication:** Required (Admin)

**URL Parameters:**
- `affiliate_id`: The affiliate's ID

**Request Body:**
```json
{
  "commissionRate": 30.0
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Commission rate updated",
  "affiliate": {
    "id": "507f1f77bcf86cd799439011",
    "commissionRate": "30.0"
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Affiliate not found"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 9. Suspend Affiliate
Suspend/deactivate an affiliate (admin only).

**Endpoint:** `PUT /api/affiliate/{affiliate_id}/suspend/`

**Authentication:** Required (Admin)

**URL Parameters:**
- `affiliate_id`: The affiliate's ID

**Success Response (200):**
```json
{
  "success": true,
  "message": "Affiliate suspended"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Affiliate not found"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 10. Get Payout Requests
Get all affiliate payout requests (admin only).

**Endpoint:** `GET /api/affiliate/payout-requests/`

**Authentication:** Required (Admin)

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`)

**Example:** `GET /api/affiliate/payout-requests/?page=1&limit=20&status=pending`

**Success Response (200):**
```json
{
  "success": true,
  "payoutRequests": [
    {
      "_id": "507f1f77bcf86cd799439015",
      "affiliateId": "507f1f77bcf86cd799439011",
      "affiliateName": "John Doe",
      "amount": 500.00,
      "Requested Date": "2024-01-15T10:30:00.000Z",
      "Payment Method": "Bank Transfer",
      "Status": "pending",
      "accountDetails": "123456789",
      "rejectionReason": null
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 2,
    "totalItems": 30
  }
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 11. Approve Payout Request
Approve an affiliate payout request (admin only).

**Endpoint:** `PUT /api/affiliate/payout-requests/{payout_id}/approve/`

**Authentication:** Required (Admin)

**URL Parameters:**
- `payout_id`: The payout request ID

**Success Response (200):**
```json
{
  "success": true,
  "message": "Payout approved"
}
```

**Note:** When a payout is approved:
- The payout amount is moved from `pending_earnings` to `paid_earnings`
- The payout status is updated to `approved`
- The `reviewed_at` and `reviewed_by` fields are set

**Error Response (404):**
```json
{
  "success": false,
  "error": "Payout request not found"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 12. Reject Payout Request
Reject an affiliate payout request (admin only).

**Endpoint:** `PUT /api/affiliate/payout-requests/{payout_id}/reject/`

**Authentication:** Required (Admin)

**URL Parameters:**
- `payout_id`: The payout request ID

**Request Body:**
```json
{
  "reason": "Insufficient documentation"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Payout rejected"
}
```

**Note:** When a payout is rejected:
- The payout status is updated to `rejected`
- The `rejection_reason` is saved
- The `reviewed_at` and `reviewed_by` fields are set
- The pending earnings remain unchanged (not deducted)

**Error Response (404):**
```json
{
  "success": false,
  "error": "Payout request not found"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

## Affiliate Signup (Authentication Endpoint)

Affiliate signup is handled through the authentication endpoints:

**Endpoint:** `POST /api/auth/affiliate/signup/`

See the authentication API documentation for details.

---

## Data Models

### Affiliate Model
```json
{
  "id": "ObjectId",
  "full_name": "string",
  "email": "string (unique)",
  "phone": "string",
  "country_code": "string",
  "affiliate_code": "string (unique)",
  "commission_rate": "string (e.g., '25.0')",
  "code_usage_count": "string (e.g., '15')",
  "total_earnings": "string (e.g., '1500.50')",
  "pending_earnings": "string (e.g., '500.25')",
  "paid_earnings": "string (e.g., '1000.25')",
  "status": "active | deactivated",
  "bank_name": "string",
  "account_number": "string",
  "iban": "string",
  "account_holder_name": "string",
  "profile_image": "string (URL)",
  "last_activity": "ISO 8601 datetime",
  "created_at": "ISO 8601 datetime"
}
```

### Affiliate Transaction Model
```json
{
  "id": "ObjectId",
  "affiliate_id": "ObjectId (Reference)",
  "affiliate_name": "string",
  "referred_user_id": "ObjectId (Reference)",
  "referred_user_name": "string",
  "transaction_id": "ObjectId (Reference to Order)",
  "commission_rate": "float",
  "commission_amount": "float",
  "status": "pending | paid",
  "date": "ISO 8601 datetime"
}
```

### Affiliate Payout Request Model
```json
{
  "id": "ObjectId",
  "affiliate_id": "ObjectId (Reference)",
  "affiliate_name": "string",
  "amount": "float",
  "requested_date": "ISO 8601 datetime",
  "payment_method": "Bank Transfer | PayPal | Crypto",
  "status": "pending | approved | rejected",
  "account_details": "string",
  "rejection_reason": "string (nullable)",
  "reviewed_at": "ISO 8601 datetime (nullable)",
  "reviewed_by": "string (admin ID, nullable)"
}
```

---

## Error Codes

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Notes

1. **Earnings Flow:**
   - Earnings are added to `total_earnings` and `pending_earnings` when payment is completed
   - Transaction status remains `pending` until buyer reviews AND seller uploads shipment proof
   - When transaction is fully completed, status changes to `paid`
   - Payout requests can only be made from `pending_earnings`
   - When payout is approved, amount moves from `pending_earnings` to `paid_earnings`

2. **Commission Rate:**
   - Stored as string in database (e.g., "25.0")
   - Represents percentage of platform fee
   - Can be updated by admin per affiliate

3. **Status Values:**
   - Affiliate status: `active`, `deactivated`
   - Transaction status: `pending`, `paid`
   - Payout status: `pending`, `approved`, `rejected`

4. **Pagination:**
   - Default page: 1
   - Default limit: 20
   - Pagination info included in response

5. **Image Upload:**
   - Profile images can be sent as base64 encoded strings
   - Format: `data:image/jpeg;base64,...` or `data:image/png;base64,...`
   - Images are processed and stored on the server

---

## Example Usage

### JavaScript/TypeScript (Axios)
```javascript
// Validate affiliate code
const validateCode = async (code) => {
  const response = await axios.post(
    'https://dolabb-backend-2vsj.onrender.com/api/affiliate/validate-code/',
    { code }
  );
  return response.data;
};

// Get affiliate profile
const getProfile = async (token) => {
  const response = await axios.get(
    'https://dolabb-backend-2vsj.onrender.com/api/affiliate/profile/',
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};

// Request cashout
const requestCashout = async (token, amount) => {
  const response = await axios.post(
    'https://dolabb-backend-2vsj.onrender.com/api/affiliate/cashout/',
    { amount, paymentMethod: 'Bank Transfer' },
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};
```

---

## Support

For issues or questions, contact the development team.

