# Frontend Changes Required for Affiliate System

This document outlines the necessary frontend changes for the updated affiliate
system.

## 1. Affiliate Code Changes

### Short Affiliate Codes

- **Change**: Affiliate codes are now 6-8 characters (alphanumeric uppercase)
  instead of `AFF-XXXXXX` format
- **Example**: `ABC123`, `XYZ7890`, `DEF4567`
- **Action Required**:
  - Update UI to display shorter codes
  - Update any validation logic if needed
  - Update referral link generation: `https://dolabb.com?ref={affiliate_code}`

## 2. Welcome Email Enhancement

### Email Content

- **Change**: Welcome email now includes affiliate code and usage guide
- **Action Required**:
  - No frontend changes needed (email is sent automatically)
  - Users will receive email with:
    - Their affiliate code prominently displayed
    - Step-by-step usage guide
    - Referral link format

## 3. Bank Details Management

### New Separate API Endpoint

#### Endpoint: `GET /api/affiliates/bank-details/`

**Description**: Get affiliate bank details

**Response:**

```json
{
  "success": true,
  "bank_details": {
    "bank_name": "Bank Name",
    "account_number": "1234567890",
    "iban": "SA1234567890123456789012",
    "account_holder_name": "John Doe"
  }
}
```

#### Endpoint: `POST /api/affiliates/bank-details/`

**Description**: Add or update bank details

**Request Body:**

```json
{
  "bank_name": "Bank Name", // Required
  "account_number": "1234567890", // Required
  "iban": "SA1234567890123456789012", // Optional
  "account_holder_name": "John Doe" // Optional (defaults to full_name)
}
```

**Response:**

```json
{
  "success": true,
  "message": "Bank details saved successfully",
  "bank_details": {
    "bank_name": "Bank Name",
    "account_number": "1234567890",
    "iban": "SA1234567890123456789012",
    "account_holder_name": "John Doe"
  }
}
```

**Error Response (Missing Required Fields):**

```json
{
  "success": false,
  "error": "Bank name is required"
}
```

#### Endpoint: `PUT /api/affiliates/bank-details/`

**Description**: Update bank details (same as POST)

**Action Required:**

- Create a new page/section for bank details management
- Add form with fields: bank_name, account_number, iban, account_holder_name
- Implement GET to fetch current bank details
- Implement POST/PUT to save/update bank details
- Show success notification when bank details are updated

## 4. Affiliate Signup Changes

### Removed Bank Fields from Signup

- **Change**: Bank details are no longer required during signup
- **Removed Fields**:
  - `bank_name`
  - `account_number`
  - `iban`
  - `account_holder_name`

**Updated Signup Request:**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "password": "password123",
  "country_code": "US",
  "profile_image_url": "https://..." // Optional
}
```

**Updated Signup Response:**

```json
{
  "success": true,
  "message": "Affiliate registered successfully...",
  "affiliate": {
    "id": "...",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "affiliate_code": "ABC123",
    "profile_image": "...",
    "total_earnings": "0",
    "total_commissions": "0",
    "code_usage_count": "0",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "otp": "1234"
}
```

**Action Required:**

- Remove bank details fields from affiliate signup form
- Update signup API call to exclude bank fields
- Update UI to handle response without bank_details

## 5. Profile Response Changes

### Removed Bank Details from Profile Response

- **Change**: Bank details are no longer included in profile GET response
- **Removed from Response**:
  - `bank_details` object

**Updated Profile Response (`GET /api/affiliates/profile/`):**

```json
{
  "success": true,
  "affiliate": {
    "id": "...",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "country_code": "US",
    "affiliate_code": "ABC123",
    "profile_image": "...",
    "totalEarnings": 100.5,
    "pendingEarnings": 50.25,
    "paidEarnings": 50.25,
    "earningsByCurrency": {
      "SAR": {
        "total": 100.5,
        "pending": 50.25,
        "paid": 50.25
      }
    },
    "codeUsageCount": 10,
    "availableBalance": 50.25,
    "commission_rate": 25.0,
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "last_activity": "2024-01-01T00:00:00Z"
  }
}
```

**Action Required:**

- Remove bank_details display from profile page
- Update profile component to not expect bank_details
- Use separate bank-details endpoint to fetch/display bank information

## 6. Profile Update Changes

### Removed Bank Fields from Profile Update

- **Change**: Bank details cannot be updated via profile endpoint
- **Profile Update Endpoint** (`PUT /api/affiliates/profile/`) now only accepts:
  - `full_name`
  - `phone`
  - `country_code`
  - `profile_image` / `profile_image_url`

**Action Required:**

- Remove bank fields from profile update form
- Use separate bank-details endpoint for updating bank information

## 7. Cashout Validation

### Bank Details Required for Cashout

- **Change**: Cashout now requires bank details to be set
- **Error Response** (when bank details missing):

```json
{
  "success": false,
  "error": "Bank details are required to request cashout. Please add your bank details first.",
  "missing_bank_details": true
}
```

**Action Required:**

- Check for `missing_bank_details` flag in cashout error response
- Show user-friendly message prompting to add bank details
- Redirect to bank details page/form if bank details are missing
- Consider disabling cashout button if bank details are not set

## 8. Implementation Checklist

- [ ] Update affiliate signup form (remove bank fields)
- [ ] Update affiliate signup API call
- [ ] Create bank details management page/component
- [ ] Implement GET bank details API call
- [ ] Implement POST/PUT bank details API call
- [ ] Update profile page (remove bank details display)
- [ ] Update profile update form (remove bank fields)
- [ ] Update cashout flow to check for bank details
- [ ] Update affiliate code display (shorter format)
- [ ] Update referral link generation
- [ ] Test complete flow: signup → add bank details → cashout

## 9. API Endpoints Summary

### Affiliate Endpoints

- `POST /api/affiliates/signup/` - Signup (no bank fields)
- `GET /api/affiliates/profile/` - Get profile (no bank_details)
- `PUT /api/affiliates/profile/` - Update profile (no bank fields)
- `GET /api/affiliates/bank-details/` - Get bank details (NEW)
- `POST /api/affiliates/bank-details/` - Add/Update bank details (NEW)
- `PUT /api/affiliates/bank-details/` - Update bank details (NEW)
- `POST /api/affiliates/cashout/` - Request cashout (validates bank details)

## 10. User Flow

### New Affiliate Flow:

1. User signs up (no bank details required)
2. User verifies OTP
3. User receives welcome email with affiliate code
4. User can start sharing affiliate code
5. User adds bank details when ready (via bank-details endpoint)
6. User can request cashout (only if bank details are set)

### Recommended UI Flow:

1. After signup/verification, show onboarding:
   - Display affiliate code prominently
   - Show usage instructions
   - Option to add bank details now or later
2. In dashboard:
   - Show affiliate code
   - Show earnings
   - Show "Add Bank Details" button if not set
   - Enable/disable cashout button based on bank details status
