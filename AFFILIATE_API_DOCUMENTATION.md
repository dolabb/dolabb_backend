# Dolabb Affiliate API Documentation

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
2. [Affiliate Management](#affiliate-management-endpoints)
3. [Transactions & Earnings](#transactions--earnings-endpoints)
4. [Payouts](#payouts-endpoints)
5. [Error Handling](#error-handling)
6. [Toast Messages](#toast-messages)

---

## Authentication Endpoints

### 1. Affiliate Signup

**Endpoint:** `POST /api/auth/affiliate/signup/`

**Request Body:**

```json
{
  "full_name": "Affiliate Name",
  "email": "affiliate@example.com",
  "phone": "+1234567890",
  "password": "password123",
  "country_code": "US",
  "bank_name": "Bank Name",
  "account_number": "123456789",
  "iban": "IBAN123",
  "account_holder_name": "Affiliate Name",
  "profile_image_url": "https://example.com/image.jpg"
}
```

**Note:** `profile_image_url` can be either:

- A URL to an existing image
- A base64 encoded image string (will be automatically converted to URL)

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Affiliate registered successfully. OTP sent to email. Please verify OTP to complete registration.",
  "affiliate": {
    "id": "affiliate_id",
    "full_name": "Affiliate Name",
    "email": "affiliate@example.com",
    "phone": "+1234567890",
    "affiliate_code": "AFF123",
    "profile_image": "https://example.com/image.jpg",
    "bank_details": {
      "bank_name": "Bank Name",
      "account_number": "123456789",
      "iban": "IBAN123",
      "account_holder_name": "Affiliate Name"
    },
    "total_earnings": 0,
    "total_commissions": 0,
    "code_usage_count": 0,
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "otp": "1234"
}
```

**Toast Message:**
`"Affiliate registration successful! Please check your email for OTP verification."`

---

### 2. Affiliate Login

**Endpoint:** `POST /api/auth/affiliate/login/`

**Request Body:**

```json
{
  "email": "affiliate@example.com",
  "password": "password123"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "affiliate": {
    "id": "affiliate_id",
    "full_name": "Affiliate Name",
    "email": "affiliate@example.com",
    "phone": "+1234567890",
    "affiliate_code": "AFF123",
    "profile_image": "https://example.com/image.jpg",
    "totalEarnings": 1000.0,
    "totalCommissions": 1000.0,
    "pendingEarnings": 500.0,
    "paidEarnings": 500.0,
    "codeUsageCount": 50,
    "availableBalance": 500.0,
    "status": "active",
    "commission_rate": 25.0,
    "bank_details": {
      "bank_name": "Bank Name",
      "account_number": "123456789",
      "iban": "IBAN123",
      "account_holder_name": "Affiliate Name"
    }
  },
  "token": "jwt_token_here"
}
```

**Toast Message:** `"Welcome back, {full_name}!"`

---

### 3. Verify OTP (Affiliate)

**Endpoint:** `POST /api/auth/affiliate/verify-otp/`

**Request Body:**

```json
{
  "email": "affiliate@example.com",
  "otp": "1234"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "OTP verified successfully",
  "affiliate": {
    "id": "affiliate_id",
    "full_name": "Affiliate Name",
    "email": "affiliate@example.com",
    "phone": "+1234567890",
    "affiliate_code": "AFF123",
    "profile_image": "https://example.com/image.jpg",
    "status": "active"
  },
  "token": "jwt_token_here"
}
```

**Toast Message:** `"Email verified successfully! Your account is now active."`

---

### 4. Resend OTP (Affiliate)

**Endpoint:** `POST /api/auth/resend-otp/`

**Request Body:**

```json
{
  "email": "affiliate@example.com",
  "user_type": "affiliate"
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

## Affiliate Management Endpoints

### 5. Get Affiliate Profile

**Endpoint:** `GET /api/affiliate/profile/`

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "affiliate": {
    "id": "affiliate_id",
    "full_name": "Affiliate Name",
    "email": "affiliate@example.com",
    "phone": "+1234567890",
    "country_code": "US",
    "affiliate_code": "AFF123",
    "profile_image": "https://example.com/image.jpg",
    "totalEarnings": 1000.0,
    "totalCommissions": 1000.0,
    "pendingEarnings": 500.0,
    "paidEarnings": 500.0,
    "codeUsageCount": 50,
    "availableBalance": 500.0,
    "commission_rate": 25.0,
    "status": "active",
    "bank_details": {
      "bank_name": "Bank Name",
      "account_number": "123456789",
      "iban": "IBAN123",
      "account_holder_name": "Affiliate Name"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "last_activity": "2024-01-01T00:00:00Z"
  }
}
```

**Response (401 Unauthorized):**

```json
{
  "success": false,
  "error": "Unauthorized. Affiliate access required."
}
```

**Toast Message:** `"Profile loaded successfully"`

---

### 6. Update Affiliate Profile

**Endpoint:** `PUT /api/affiliate/profile/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "full_name": "Updated Name",
  "phone": "+1234567890",
  "country_code": "US",
  "profile_image": "https://example.com/image.jpg",
  "bank_name": "Bank Name",
  "account_number": "123456789",
  "iban": "IBAN123",
  "account_holder_name": "Affiliate Name"
}
```

**Note:**

- All fields are optional - only include fields you want to update
- `profile_image` can be either:
  - A URL to an existing image
  - A base64 encoded image string (will be automatically converted to URL)

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "affiliate": {
    "id": "affiliate_id",
    "full_name": "Updated Name",
    "email": "affiliate@example.com",
    "phone": "+1234567890",
    "country_code": "US",
    "affiliate_code": "AFF123",
    "profile_image": "https://example.com/image.jpg",
    "totalEarnings": 1000.0,
    "totalCommissions": 1000.0,
    "pendingEarnings": 500.0,
    "paidEarnings": 500.0,
    "codeUsageCount": 50,
    "availableBalance": 500.0,
    "commission_rate": 25.0,
    "status": "active",
    "bank_details": {
      "bank_name": "Bank Name",
      "account_number": "123456789",
      "iban": "IBAN123",
      "account_holder_name": "Affiliate Name"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "last_activity": "2024-01-01T00:00:00Z"
  }
}
```

**Response (401 Unauthorized):**

```json
{
  "success": false,
  "error": "Unauthorized. Affiliate access required."
}
```

**Toast Message:** `"Profile updated successfully!"`

---

### 7. Validate Affiliate Code

**Endpoint:** `POST /api/affiliate/validate-code/`

**Request Body:**

```json
{
  "code": "AFF123"
}
```

**Response (200 OK):**

```json
{
  "valid": true,
  "message": "Affiliate code is valid",
  "affiliate": {
    "id": "affiliate_id",
    "full_name": "Affiliate Name",
    "affiliate_code": "AFF123"
  }
}
```

**Response (400 Bad Request) - Invalid Code:**

```json
{
  "valid": false,
  "message": "Invalid affiliate code"
}
```

---

## Transactions & Earnings Endpoints

### 8. Get Affiliate Transactions

**Endpoint:** `GET /api/affiliate/{affiliate_id}/transactions/`

**Headers:**

```
Authorization: Bearer <token>
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
      "referredUserId": "user_id",
      "referredUserName": "User Name",
      "commission": 10.0,
      "commissionRate": 25.0,
      "status": "paid",
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

**Note:** This endpoint is typically used by admins. Affiliates can view their
earnings through the login response.

---

## Payouts Endpoints

### 9. Request Cashout

**Endpoint:** `POST /api/affiliate/cashout/`

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "amount": 500.0,
  "paymentMethod": "Bank Transfer"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "cashoutRequest": {
    "id": "cashout_id",
    "affiliateId": "affiliate_id",
    "amount": 500.0,
    "status": "pending",
    "requestedAt": "2024-01-01T00:00:00Z"
  }
}
```

**Response (400 Bad Request) - Insufficient Balance:**

```json
{
  "success": false,
  "error": "Insufficient balance. Available balance is 300.0"
}
```

**Toast Message:** `"Cashout request submitted! Waiting for admin approval."`

---

### 10. Get Payout Requests

**Endpoint:** `GET /api/affiliate/payout-requests/`

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
{
  "success": true,
  "payoutRequests": [
    {
      "id": "payout_id",
      "affiliateId": "affiliate_id",
      "affiliateName": "Affiliate Name",
      "amount": 500.0,
      "status": "pending",
      "paymentMethod": "Bank Transfer",
      "requestedAt": "2024-01-01T00:00:00Z",
      "processedAt": null,
      "notes": ""
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50
  }
}
```

**Note:** This endpoint is typically used by admins to view all payout requests.

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

### Common Error Scenarios:

| Error Type             | Message                                               | Status Code |
| ---------------------- | ----------------------------------------------------- | ----------- |
| Invalid Credentials    | "Invalid email or password. Please try again."        | 401         |
| OTP Expired            | "OTP has expired. Please request a new one."          | 400         |
| Invalid OTP            | "Invalid OTP. Please check and try again."            | 400         |
| Email Already Exists   | "Affiliate with this email already exists"            | 400         |
| Invalid Affiliate Code | "Invalid affiliate code"                              | 400         |
| Insufficient Balance   | "Insufficient balance. Available balance is {amount}" | 400         |
| Account Suspended      | "Affiliate account is deactivated"                    | 403         |
| Unauthorized           | "Session expired. Please login again."                | 401         |

---

## Toast Messages

### Success Messages

| Action            | Message                                                                            |
| ----------------- | ---------------------------------------------------------------------------------- |
| Affiliate Signup  | "Affiliate registration successful! Please check your email for OTP verification." |
| Affiliate Login   | "Welcome back, {full_name}!"                                                       |
| OTP Verified      | "Email verified successfully! Your account is now active."                         |
| OTP Resent        | "OTP has been resent to your email."                                               |
| Profile Updated   | "Profile updated successfully!"                                                    |
| Cashout Requested | "Cashout request submitted! Waiting for admin approval."                           |
| Code Validated    | "Affiliate code is valid"                                                          |

### Error Messages

| Error Type             | Message                                                      |
| ---------------------- | ------------------------------------------------------------ |
| Invalid Credentials    | "Invalid email or password. Please try again."               |
| OTP Expired            | "OTP has expired. Please request a new one."                 |
| Invalid OTP            | "Invalid OTP. Please check and try again."                   |
| Email Already Exists   | "This email is already registered. Please login instead."    |
| Invalid Affiliate Code | "Invalid affiliate code. Please check and try again."        |
| Insufficient Balance   | "Insufficient balance for this transaction."                 |
| Account Suspended      | "Affiliate account is deactivated. Please contact support."  |
| Network Error          | "Network error. Please check your connection and try again." |
| Unauthorized           | "Session expired. Please login again."                       |

### Info Messages

| Action             | Message                              |
| ------------------ | ------------------------------------ |
| Loading            | "Please wait..."                     |
| Processing Cashout | "Processing your cashout request..." |

---

## Affiliate Code Usage

### How Affiliate Codes Work

1. **Code Generation**: Each affiliate receives a unique code upon registration
   (e.g., `AFF123`)
2. **Code Usage**: Users can enter affiliate codes during checkout
3. **Commission Calculation**: Affiliates earn a percentage of the platform fee
   from orders using their code
4. **Earnings Tracking**: All earnings are tracked and displayed in the
   affiliate dashboard

### Commission Structure

- **Default Commission Rate**: 25% of platform fee (configurable by admin)
- **Individual Commission Rate**: Admins can set custom rates per affiliate
- **Commission Payment**: Commissions are added to pending earnings when payment
  is completed

### Example Flow

1. User enters affiliate code `AFF123` at checkout
2. Order is created with the affiliate code
3. When payment is completed, commission is calculated
4. Commission is added to affiliate's pending earnings
5. Affiliate can request cashout when ready

---

## Notes

1. **Token Storage**: Store JWT token in `localStorage` or `sessionStorage` for
   persistence
2. **Token Refresh**: Implement token refresh logic if tokens expire
3. **Image URLs**: Profile images can be URLs or base64 strings (automatically
   converted)
4. **Earnings**: Earnings are only updated when order payment is completed
5. **Payout Status**: Payout requests require admin approval before processing
6. **Commission Rates**: Default rate is 25%, but admins can set individual
   rates
7. **Code Validation**: Always validate affiliate codes before allowing checkout
8. **Error Handling**: Always check `success` field in responses before
   processing data
9. **Loading States**: Show loading indicators during API calls
10. **Balance Check**: Always verify available balance before requesting cashout

---

## Support

For API support or questions, contact the development team.

**Base URL:** `https://dolabb-backend-2vsj.onrender.com`

---

## Related Documentation

- [Website API Documentation](./WEBSITE_API_DOCUMENTATION.md) - For general user
  and product APIs
- [Admin Dashboard API Documentation](./ADMIN_DASHBOARD_API_DOCUMENTATION.md) -
  For admin-specific affiliate management
