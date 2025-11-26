# Seller Sale History & Payout Integration Guide

This guide provides step-by-step instructions for integrating the Seller Sale History and Payout Management features into your frontend application.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Frontend Integration](#frontend-integration)
5. [Error Handling](#error-handling)
6. [Complete Example](#complete-example)

---

## Overview

The Seller Sale History & Payout system consists of four main features:

1. **Sale History** - View all sales/payments with order details
2. **Earnings Summary** - View total earnings, payouts, and available balance
3. **Payout Request** - Request withdrawal of available balance
4. **Payout History** - View all payout requests and their status

---

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```javascript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

**Note:** Only users with `role: 'seller'` can access these endpoints.

---

## API Endpoints

### Base URL

```
https://dolabb-backend-2vsj.onrender.com
```

### 1. Get Sale History

**Endpoint:** `GET /api/user/payments/`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `paid`, `shipped`, `delivered`, `cancelled`)

**Response:**
```json
{
  "payments": [
    {
      "id": "order_id",
      "orderNumber": "ORD-12345",
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
      "orderDate": "2024-01-15T10:30:00Z",
      "status": "delivered",
      "totalPrice": 150.0,
      "platformFee": 15.0,
      "sellerPayout": 135.0,
      "affiliateCode": "AFF123",
      "shippingAddress": {
        "fullName": "John Doe",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "Riyadh",
        "postalCode": "12345",
        "country": "Saudi Arabia",
        "additionalInfo": "Apt 4B"
      },
      "trackingNumber": "TRACK123456"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 47
  }
}
```

---

### 2. Get Earnings Summary

**Endpoint:** `GET /api/seller/earnings/`

**Response:**
```json
{
  "success": true,
  "earnings": {
    "totalEarnings": 5000.0,
    "totalPayouts": 3000.0,
    "pendingPayouts": 500.0,
    "availableBalance": 1500.0
  }
}
```

---

### 3. Request Payout

**Endpoint:** `POST /api/seller/payout/request/`

**Request Body:**
```json
{
  "amount": 500.0,
  "paymentMethod": "Bank Transfer"
}
```

**Payment Methods:**
- `Bank Transfer`
- `PayPal`
- `Stripe`

**Success Response (201):**
```json
{
  "success": true,
  "payoutRequest": {
    "id": "payout_request_id",
    "sellerId": "seller_id",
    "amount": 500.0,
    "status": "pending",
    "paymentMethod": "Bank Transfer",
    "requestedAt": "2024-01-15T10:30:00Z",
    "processedAt": null,
    "notes": null
  }
}
```

**Error Responses:**

- **400 Bad Request** - Amount exceeds available balance:
```json
{
  "success": false,
  "error": "Amount exceeds available balance"
}
```

- **400 Bad Request** - Invalid amount:
```json
{
  "success": false,
  "error": "Invalid amount. Amount must be greater than 0"
}
```

---

### 4. Get Payout Requests History

**Endpoint:** `GET /api/seller/payout-requests/`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`)

**Response:**
```json
{
  "success": true,
  "payoutRequests": [
    {
      "id": "payout_request_id",
      "sellerId": "seller_id",
      "amount": 500.0,
      "status": "pending",
      "paymentMethod": "Bank Transfer",
      "requestedAt": "2024-01-15T10:30:00Z",
      "processedAt": null,
      "notes": null
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 2,
    "totalItems": 15
  }
}
```

---

## Frontend Integration

### Step 1: Setup API Client

Create an API client utility (using Axios example):

```javascript
// utils/api.js
import axios from 'axios';

const API_BASE_URL = 'https://dolabb-backend-2vsj.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

---

### Step 2: Create API Functions

```javascript
// api/sellerApi.js
import api from '../utils/api';

// Get sale history
export const getSaleHistory = async (params = {}) => {
  const { page = 1, limit = 20, status } = params;
  const queryParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  
  if (status) {
    queryParams.append('status', status);
  }
  
  const response = await api.get(`/api/user/payments/?${queryParams}`);
  return response.data;
};

// Get earnings summary
export const getSellerEarnings = async () => {
  const response = await api.get('/api/seller/earnings/');
  return response.data;
};

// Request payout
export const requestPayout = async (data) => {
  const response = await api.post('/api/seller/payout/request/', data);
  return response.data;
};

// Get payout requests
export const getPayoutRequests = async (params = {}) => {
  const { page = 1, limit = 20, status } = params;
  const queryParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  
  if (status) {
    queryParams.append('status', status);
  }
  
  const response = await api.get(`/api/seller/payout-requests/?${queryParams}`);
  return response.data;
};
```

---

### Step 3: React Query / RTK Query Integration

#### Using React Query:

```javascript
// hooks/useSellerApi.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getSaleHistory,
  getSellerEarnings,
  requestPayout,
  getPayoutRequests,
} from '../api/sellerApi';

// Sale History
export const useSaleHistory = (params) => {
  return useQuery({
    queryKey: ['saleHistory', params],
    queryFn: () => getSaleHistory(params),
  });
};

// Earnings Summary
export const useSellerEarnings = () => {
  return useQuery({
    queryKey: ['sellerEarnings'],
    queryFn: getSellerEarnings,
    refetchOnWindowFocus: true,
  });
};

// Payout Requests
export const usePayoutRequests = (params) => {
  return useQuery({
    queryKey: ['payoutRequests', params],
    queryFn: () => getPayoutRequests(params),
  });
};

// Request Payout Mutation
export const useRequestPayout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: requestPayout,
    onSuccess: () => {
      // Invalidate and refetch earnings and payout requests
      queryClient.invalidateQueries(['sellerEarnings']);
      queryClient.invalidateQueries(['payoutRequests']);
    },
  });
};
```

#### Using RTK Query:

```javascript
// api/sellerApiSlice.js
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_BASE_URL = 'https://dolabb-backend-2vsj.onrender.com';

export const sellerApi = createApi({
  reducerPath: 'sellerApi',
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = getState().auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Earnings', 'PayoutRequests', 'SaleHistory'],
  endpoints: (builder) => ({
    getSaleHistory: builder.query({
      query: (params = {}) => {
        const { page = 1, limit = 20, status } = params;
        const queryParams = new URLSearchParams({
          page: page.toString(),
          limit: limit.toString(),
        });
        if (status) queryParams.append('status', status);
        return `/api/user/payments/?${queryParams}`;
      },
      providesTags: ['SaleHistory'],
    }),
    getSellerEarnings: builder.query({
      query: () => '/api/seller/earnings/',
      providesTags: ['Earnings'],
    }),
    getPayoutRequests: builder.query({
      query: (params = {}) => {
        const { page = 1, limit = 20, status } = params;
        const queryParams = new URLSearchParams({
          page: page.toString(),
          limit: limit.toString(),
        });
        if (status) queryParams.append('status', status);
        return `/api/seller/payout-requests/?${queryParams}`;
      },
      providesTags: ['PayoutRequests'],
    }),
    requestPayout: builder.mutation({
      query: (data) => ({
        url: '/api/seller/payout/request/',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Earnings', 'PayoutRequests'],
    }),
  }),
});

export const {
  useGetSaleHistoryQuery,
  useGetSellerEarningsQuery,
  useGetPayoutRequestsQuery,
  useRequestPayoutMutation,
} = sellerApi;
```

---

### Step 4: Create React Components

#### Sale History Component

```jsx
// components/SaleHistoryTab.jsx
import React, { useState } from 'react';
import { useSaleHistory } from '../hooks/useSellerApi';

const SaleHistoryTab = () => {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  
  const { data, isLoading, error } = useSaleHistory({
    page,
    limit: 10,
    status: statusFilter || undefined,
  });
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  const { payments, pagination } = data || {};
  
  return (
    <div>
      <h2>Sale History</h2>
      
      {/* Status Filter */}
      <select
        value={statusFilter}
        onChange={(e) => {
          setStatusFilter(e.target.value);
          setPage(1);
        }}
      >
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="paid">Paid</option>
        <option value="shipped">Shipped</option>
        <option value="delivered">Delivered</option>
        <option value="cancelled">Cancelled</option>
      </select>
      
      {/* Payments List */}
      <div>
        {payments?.map((payment) => (
          <div key={payment.id} className="payment-card">
            <img
              src={payment.product.images[0]}
              alt={payment.product.title}
              width={100}
            />
            <div>
              <h3>{payment.product.title}</h3>
              <p>Order: {payment.orderNumber}</p>
              <p>Buyer: {payment.buyer.username}</p>
              <p>Date: {new Date(payment.orderDate).toLocaleDateString()}</p>
              <p>Total Price: {payment.totalPrice} SAR</p>
              <p>Platform Fee: {payment.platformFee} SAR</p>
              <p>Seller Payout: {payment.sellerPayout} SAR</p>
              <span className={`status-badge status-${payment.status}`}>
                {payment.status}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Pagination */}
      <div>
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          Previous
        </button>
        <span>
          Page {pagination?.currentPage} of {pagination?.totalPages}
        </span>
        <button
          disabled={page >= pagination?.totalPages}
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default SaleHistoryTab;
```

#### Payout Tab Component

```jsx
// components/PayoutTab.jsx
import React, { useState } from 'react';
import {
  useSellerEarnings,
  usePayoutRequests,
  useRequestPayout,
} from '../hooks/useSellerApi';

const PayoutTab = () => {
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Bank Transfer');
  const [page, setPage] = useState(1);
  
  const { data: earningsData, isLoading: earningsLoading } = useSellerEarnings();
  const { data: payoutData, isLoading: payoutLoading } = usePayoutRequests({
    page,
    limit: 20,
  });
  
  const requestPayoutMutation = useRequestPayout();
  
  const earnings = earningsData?.earnings || {};
  const payoutRequests = payoutData?.payoutRequests || [];
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payoutAmount = parseFloat(amount);
    
    // Validation
    if (payoutAmount <= 0) {
      alert('Amount must be greater than 0');
      return;
    }
    
    if (payoutAmount > earnings.availableBalance) {
      alert('Amount exceeds available balance');
      return;
    }
    
    try {
      await requestPayoutMutation.mutateAsync({
        amount: payoutAmount,
        paymentMethod,
      });
      alert('Payout request submitted successfully!');
      setAmount('');
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to submit payout request');
    }
  };
  
  if (earningsLoading) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>Payout Management</h2>
      
      {/* Earnings Summary Cards */}
      <div className="earnings-grid">
        <div className="earnings-card">
          <h3>Total Earnings</h3>
          <p className="amount">{earnings.totalEarnings} SAR</p>
        </div>
        <div className="earnings-card">
          <h3>Total Payouts</h3>
          <p className="amount">{earnings.totalPayouts} SAR</p>
        </div>
        <div className="earnings-card">
          <h3>Pending Payouts</h3>
          <p className="amount">{earnings.pendingPayouts} SAR</p>
        </div>
        <div className="earnings-card highlight">
          <h3>Available Balance</h3>
          <p className="amount">{earnings.availableBalance} SAR</p>
        </div>
      </div>
      
      {/* Payout Request Form */}
      <div className="payout-form">
        <h3>Request Payout</h3>
        <form onSubmit={handleSubmit}>
          <div>
            <label>Amount (SAR)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max={earnings.availableBalance}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
            <small>Available: {earnings.availableBalance} SAR</small>
          </div>
          
          <div>
            <label>Payment Method</label>
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              required
            >
              <option value="Bank Transfer">Bank Transfer</option>
              <option value="PayPal">PayPal</option>
              <option value="Stripe">Stripe</option>
            </select>
          </div>
          
          <button
            type="submit"
            disabled={
              requestPayoutMutation.isLoading ||
              !amount ||
              parseFloat(amount) <= 0 ||
              parseFloat(amount) > earnings.availableBalance
            }
          >
            {requestPayoutMutation.isLoading ? 'Submitting...' : 'Request Payout'}
          </button>
        </form>
      </div>
      
      {/* Payout Requests History */}
      <div className="payout-history">
        <h3>Payout Requests History</h3>
        {payoutLoading ? (
          <div>Loading...</div>
        ) : (
          <div>
            {payoutRequests.map((request) => (
              <div key={request.id} className="payout-request-card">
                <div>
                  <p><strong>Amount:</strong> {request.amount} SAR</p>
                  <p><strong>Payment Method:</strong> {request.paymentMethod}</p>
                  <p><strong>Requested:</strong> {new Date(request.requestedAt).toLocaleString()}</p>
                  {request.processedAt && (
                    <p><strong>Processed:</strong> {new Date(request.processedAt).toLocaleString()}</p>
                  )}
                  {request.notes && (
                    <p><strong>Notes:</strong> {request.notes}</p>
                  )}
                </div>
                <span className={`status-badge status-${request.status}`}>
                  {request.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PayoutTab;
```

---

## Error Handling

### Common Error Scenarios

1. **401 Unauthorized** - Token missing or invalid
   ```javascript
   if (error.response?.status === 401) {
     // Redirect to login
     localStorage.removeItem('token');
     window.location.href = '/login';
   }
   ```

2. **403 Forbidden** - User is not a seller
   ```javascript
   if (error.response?.status === 403) {
     alert('Only sellers can access this feature');
   }
   ```

3. **400 Bad Request** - Validation errors
   ```javascript
   if (error.response?.status === 400) {
     const errorMessage = error.response.data.error;
     alert(errorMessage);
   }
   ```

### Error Handler Utility

```javascript
// utils/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;
    
    switch (status) {
      case 401:
        localStorage.removeItem('token');
        window.location.href = '/login';
        return 'Session expired. Please login again.';
      
      case 403:
        return 'You do not have permission to access this resource.';
      
      case 400:
        return data.error || 'Invalid request. Please check your input.';
      
      case 404:
        return 'Resource not found.';
      
      case 500:
        return 'Server error. Please try again later.';
      
      default:
        return data.error || 'An error occurred. Please try again.';
    }
  } else if (error.request) {
    // Request made but no response
    return 'Network error. Please check your connection.';
  } else {
    // Error in request setup
    return error.message || 'An unexpected error occurred.';
  }
};
```

---

## Complete Example

### Profile Page with Tabs

```jsx
// pages/ProfilePage.jsx
import React, { useState } from 'react';
import SaleHistoryTab from '../components/SaleHistoryTab';
import PayoutTab from '../components/PayoutTab';

const ProfilePage = () => {
  const [activeTab, setActiveTab] = useState('sales');
  
  return (
    <div className="profile-page">
      <h1>Seller Dashboard</h1>
      
      {/* Tabs */}
      <div className="tabs">
        <button
          className={activeTab === 'sales' ? 'active' : ''}
          onClick={() => setActiveTab('sales')}
        >
          Sale History
        </button>
        <button
          className={activeTab === 'payout' ? 'active' : ''}
          onClick={() => setActiveTab('payout')}
        >
          Payout
        </button>
      </div>
      
      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'sales' && <SaleHistoryTab />}
        {activeTab === 'payout' && <PayoutTab />}
      </div>
    </div>
  );
};

export default ProfilePage;
```

---

## TypeScript Types

```typescript
// types/seller.ts

export interface Payment {
  id: string;
  orderNumber: string;
  product: {
    id: string;
    title: string;
    images: string[];
  };
  buyer: {
    id: string;
    username: string;
    profileImage?: string;
  };
  orderDate: string;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  totalPrice: number;
  platformFee: number;
  sellerPayout: number;
  affiliateCode?: string;
  shippingAddress: {
    fullName: string;
    phone: string;
    address: string;
    city: string;
    postalCode: string;
    country: string;
    additionalInfo?: string;
  };
  trackingNumber?: string;
}

export interface SellerEarnings {
  totalEarnings: number;
  totalPayouts: number;
  pendingPayouts: number;
  availableBalance: number;
}

export interface PayoutRequest {
  id: string;
  sellerId: string;
  amount: number;
  status: 'pending' | 'approved' | 'rejected';
  paymentMethod: 'Bank Transfer' | 'PayPal' | 'Stripe';
  requestedAt: string;
  processedAt: string | null;
  notes: string | null;
}

export interface Pagination {
  currentPage: number;
  totalPages: number;
  totalItems: number;
}
```

---

## Testing

### Test Sale History API

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/user/payments/?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Earnings API

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/seller/earnings/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Request Payout

```bash
curl -X POST "https://dolabb-backend-2vsj.onrender.com/api/seller/payout/request/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "paymentMethod": "Bank Transfer"
  }'
```

### Test Payout Requests

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/seller/payout-requests/?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Best Practices

1. **Caching**: Use React Query or RTK Query for automatic caching and refetching
2. **Loading States**: Always show loading indicators during API calls
3. **Error Handling**: Display user-friendly error messages
4. **Validation**: Validate inputs on both client and server side
5. **Pagination**: Implement proper pagination for large datasets
6. **Real-time Updates**: Consider WebSocket for real-time status updates
7. **Security**: Never expose tokens in client-side code
8. **Rate Limiting**: Implement rate limiting for payout requests

---

## Support

For issues or questions:
- Check the API documentation: `SELLER_SALE_HISTORY_PAYOUT_GUIDE.md`
- Review error responses for specific error messages
- Ensure user has seller role and valid authentication token

---

## Changelog

- **v1.0.0** (2024-01-15)
  - Initial release
  - Sale History API
  - Earnings Summary API
  - Payout Request API
  - Payout Requests History API

