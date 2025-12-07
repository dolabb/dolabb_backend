# Multi-Currency Affiliate Commission System - Implementation Guide

## Overview
The system now tracks affiliate commissions separately by currency without currency conversion. Each currency's earnings (total, pending, paid) are tracked independently.

---

## Backend Changes Made

### 1. **Database Models Updated**

#### `AffiliateTransaction` Model (`affiliates/models.py`)
- ✅ Added `currency` field (StringField, default='SAR')
- ✅ Stores the currency of each commission transaction

#### `Affiliate` Model (`authentication/models.py`)
- ✅ Added `earnings_by_currency` field (DictField)
- ✅ Format: `{"SAR": {"total": 100.0, "pending": 50.0, "paid": 50.0}, "USDT": {"total": 25.0, "pending": 25.0, "paid": 0.0}}`
- ✅ Legacy fields (`total_earnings`, `pending_earnings`, `paid_earnings`) kept for backward compatibility

#### `AffiliatePayoutRequest` Model (`affiliates/models.py`)
- ✅ Added `currency` field (StringField, default='SAR')
- ✅ Tracks which currency the payout request is for

### 2. **Commission Calculation Logic**

#### When Order is Created (`products/services.py`)
- ✅ Commission is calculated in the order's currency
- ✅ Currency is stored in `AffiliateTransaction` when transaction is created

#### When Payment is Completed (`products/services.py`)
- ✅ Earnings are updated in the currency-specific `earnings_by_currency` dict
- ✅ Legacy fields are also updated (sum of all currencies)

### 3. **API Response Changes**

All affiliate-related APIs now return:
- ✅ `earningsByCurrency`: Breakdown by currency
- ✅ Legacy fields (`totalEarnings`, `pendingEarnings`, `paidEarnings`): Sum across all currencies

---

## Frontend Changes Required

### **Affiliate Dashboard Changes**

#### 1. **Dashboard Overview Page**

**Current Display:**
```
Total Earnings: $1,250.00
Pending: $500.00
Paid: $750.00
```

**New Display (Recommended):**
```
Total Earnings: $1,250.00
├─ SAR: 1,000.00 SAR
└─ USDT: 250.00 USDT

Pending Earnings: $500.00
├─ SAR: 300.00 SAR
└─ USDT: 200.00 USDT

Paid Earnings: $750.00
├─ SAR: 700.00 SAR
└─ USDT: 50.00 USDT
```

**API Response Structure:**
```json
{
  "success": true,
  "affiliate": {
    "totalEarnings": 1250.00,
    "pendingEarnings": 500.00,
    "paidEarnings": 750.00,
    "earningsByCurrency": {
      "SAR": {
        "total": 1000.00,
        "pending": 300.00,
        "paid": 700.00
      },
      "USDT": {
        "total": 250.00,
        "pending": 200.00,
        "paid": 50.00
      }
    }
  }
}
```

#### 2. **Transactions List Page**

**Changes Needed:**
- ✅ Display currency column for each transaction
- ✅ Add currency filter (filter by SAR, USDT, etc.)
- ✅ Group transactions by currency (optional)

**API Response:**
```json
{
  "transactions": [
    {
      "_id": "...",
      "Referred User Commission": 25.00,
      "currency": "USDT",  // NEW FIELD
      "status": "pending",
      "date": "2024-01-15T10:30:00Z"
    },
    {
      "_id": "...",
      "Referred User Commission": 50.00,
      "currency": "SAR",  // NEW FIELD
      "status": "paid",
      "date": "2024-01-14T09:20:00Z"
    }
  ]
}
```

**UI Example:**
```
Transaction History
┌─────────────────────────────────────────────────────┐
│ Date       | User        | Amount    | Currency | Status │
├─────────────────────────────────────────────────────┤
│ 2024-01-15 | John Doe    | 25.00     | USDT     | Pending│
│ 2024-01-14 | Jane Smith  | 50.00     | SAR      | Paid   │
└─────────────────────────────────────────────────────┘

Filter by Currency: [All] [SAR] [USDT]
```

#### 3. **Cashout Request Page**

**Changes Needed:**
- ✅ Add currency selector dropdown
- ✅ Show available balance per currency
- ✅ Validate that requested amount doesn't exceed available balance for selected currency

**API Request:**
```json
POST /api/affiliates/request-cashout
{
  "amount": 100.00,
  "currency": "USDT",  // NEW FIELD - Required
  "paymentMethod": "Crypto"
}
```

**API Response:**
```json
{
  "success": true,
  "message": "Cashout request submitted successfully",
  "cashoutRequest": {
    "id": "...",
    "amount": 100.00,
    "currency": "USDT",
    "status": "pending"
  },
  "updatedBalance": {
    "availableBalance": 150.00,
    "pendingEarnings": 150.00,
    "currency": "USDT"
  },
  "earningsByCurrency": {
    "SAR": {"total": 1000.00, "pending": 300.00, "paid": 700.00},
    "USDT": {"total": 250.00, "pending": 150.00, "paid": 100.00}
  }
}
```

**UI Example:**
```
Request Cashout
┌─────────────────────────────────────┐
│ Currency: [USDT ▼]                  │
│ Available Balance: 200.00 USDT      │
│                                     │
│ Amount: [100.00]                    │
│ Payment Method: [Crypto ▼]          │
│                                     │
│ [Request Cashout]                   │
└─────────────────────────────────────┘

Available by Currency:
• SAR: 300.00 SAR
• USDT: 200.00 USDT
```

#### 4. **Earnings Breakdown/Graphs Page**

**Changes Needed:**
- ✅ Add currency filter/selector
- ✅ Show separate graphs for each currency (or combined with currency labels)
- ✅ Update breakdown to show currency

**API Response:**
```json
{
  "summary": {
    "totalEarnings": 1250.00,
    "pendingEarnings": 500.00,
    "paidEarnings": 750.00,
    "earningsByCurrency": {  // NEW FIELD
      "SAR": {"total": 1000.00, "pending": 300.00, "paid": 700.00},
      "USDT": {"total": 250.00, "pending": 200.00, "paid": 50.00}
    }
  },
  "breakdown": [...]
}
```

**UI Example:**
```
Earnings Overview
┌─────────────────────────────────────┐
│ View: [All Currencies ▼]            │
│ [SAR] [USDT] [All]                  │
│                                     │
│ [Graph showing earnings over time]  │
│ (with currency labels)              │
└─────────────────────────────────────┘
```

---

### **Admin Dashboard Changes**

#### 1. **All Affiliates List Page**

**Changes Needed:**
- ✅ Display currency breakdown in earnings column
- ✅ Add currency filter
- ✅ Show totals per currency

**API Response:**
```json
{
  "affiliates": [
    {
      "Affiliatename": "John Doe",
      "Earnings": {
        "Total": 1250.00,
        "Pending": 500.00,
        "Paid": 750.00
      },
      "EarningsByCurrency": {  // NEW FIELD
        "SAR": {"total": 1000.00, "pending": 300.00, "paid": 700.00},
        "USDT": {"total": 250.00, "pending": 200.00, "paid": 50.00}
      }
    }
  ]
}
```

**UI Example:**
```
All Affiliates
┌─────────────────────────────────────────────────────────────┐
│ Name      | Code    | Earnings (Total) | By Currency        │
├─────────────────────────────────────────────────────────────┤
│ John Doe  | ABC123  | 1,250.00        | SAR: 1,000.00     │
│           |         |                  | USDT: 250.00     │
└─────────────────────────────────────────────────────────────┘
```

#### 2. **Affiliate Transaction History (Admin View)**

**Changes Needed:**
- ✅ Display currency column
- ✅ Add currency filter
- ✅ Show currency in transaction details

**API Response:**
```json
{
  "transactions": [
    {
      "Transaction ID": "...",
      "Referred User Commission": 25.00,
      "currency": "USDT",  // NEW FIELD
      "status": "pending"
    }
  ]
}
```

#### 3. **Payout Requests Management**

**Changes Needed:**
- ✅ Display currency for each payout request
- ✅ Add currency filter
- ✅ Show currency in approval/rejection workflow

**API Response:**
```json
{
  "payoutRequests": [
    {
      "affiliateName": "John Doe",
      "amount": 100.00,
      "currency": "USDT",  // NEW FIELD
      "status": "pending",
      "Payment Method": "Crypto"
    }
  ]
}
```

**UI Example:**
```
Payout Requests
┌─────────────────────────────────────────────────────┐
│ Affiliate | Amount    | Currency | Method | Status │
├─────────────────────────────────────────────────────┤
│ John Doe  | 100.00    | USDT     | Crypto | Pending│
│ Jane Smith| 50.00     | SAR      | Bank   | Pending│
└─────────────────────────────────────────────────────┘
```

---

## Key Implementation Points

### 1. **Currency Handling**
- ✅ No currency conversion - amounts stay in original currency
- ✅ Each currency tracked independently
- ✅ Legacy totals are sum of all currencies (for backward compatibility)

### 2. **Cashout Requests**
- ✅ Must specify currency when requesting cashout
- ✅ System validates available balance for that specific currency
- ✅ Payout requests store currency

### 3. **Backward Compatibility**
- ✅ Legacy fields (`totalEarnings`, `pendingEarnings`, `paidEarnings`) still work
- ✅ They show sum across all currencies
- ✅ New `earningsByCurrency` field provides detailed breakdown

### 4. **Data Migration**
- ✅ Existing affiliates will have empty `earnings_by_currency` initially
- ✅ System falls back to legacy fields if `earnings_by_currency` is empty
- ✅ New transactions will populate currency-specific earnings

---

## API Endpoints Updated

All these endpoints now return `earningsByCurrency`:

1. ✅ `GET /api/affiliates/profile` - Affiliate profile
2. ✅ `GET /api/affiliates/transactions` - Transaction history
3. ✅ `GET /api/affiliates/earnings-breakdown` - Earnings breakdown
4. ✅ `GET /api/admin/affiliates` - All affiliates (admin)
5. ✅ `GET /api/admin/affiliates/{id}/transactions` - Affiliate transactions (admin)
6. ✅ `POST /api/affiliates/request-cashout` - Now requires `currency` field
7. ✅ `GET /api/affiliates/cashout-requests` - Returns currency in payout requests

---

## Testing Checklist

### Backend Testing
- [ ] Create order with USDT currency and affiliate code
- [ ] Create order with SAR currency and affiliate code
- [ ] Verify commissions are stored with correct currency
- [ ] Verify earnings_by_currency is updated correctly
- [ ] Test cashout request with currency
- [ ] Test payout approval/rejection with currency

### Frontend Testing
- [ ] Display earnings breakdown by currency
- [ ] Filter transactions by currency
- [ ] Request cashout with currency selection
- [ ] Validate cashout amount against currency-specific balance
- [ ] Display currency in admin affiliate list
- [ ] Display currency in payout requests

---

## Example Scenarios

### Scenario 1: Seller Creates Listing in USDT
1. Seller creates listing priced in USDT
2. Buyer purchases using affiliate code
3. Commission calculated in USDT
4. Affiliate's `earnings_by_currency["USDT"]` is updated
5. Transaction shows currency = "USDT"

### Scenario 2: Seller Creates Listing in SAR
1. Seller creates listing priced in SAR
2. Buyer purchases using affiliate code
3. Commission calculated in SAR
4. Affiliate's `earnings_by_currency["SAR"]` is updated
5. Transaction shows currency = "SAR"

### Scenario 3: Affiliate Requests Cashout
1. Affiliate has: 300 SAR pending, 200 USDT pending
2. Affiliate requests 100 USDT cashout
3. System validates: 200 USDT >= 100 USDT ✅
4. `earnings_by_currency["USDT"]["pending"]` reduced to 100 USDT
5. Payout request created with currency = "USDT"

---

## Notes

- **No Currency Conversion**: The system does NOT convert between currencies. Each currency is tracked separately.
- **Default Currency**: If currency is not specified, defaults to "SAR"
- **Legacy Support**: Old fields still work but show combined totals
- **Future Enhancement**: Can add currency conversion later if needed, but current implementation keeps it simple

---

## Support

If you have questions or need clarification on any part of this implementation, please refer to:
- Backend code: `affiliates/models.py`, `affiliates/services.py`, `affiliates/views.py`
- Commission logic: `products/services.py` (OrderService class)

