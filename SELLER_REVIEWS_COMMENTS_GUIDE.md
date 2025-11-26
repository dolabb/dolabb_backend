# Seller Reviews & Comments Guide

This guide documents how reviews and comments are displayed to sellers, including the APIs for viewing reviews, rating statistics, and how to integrate these features into the seller profile and tabs.

---

## Table of Contents

1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Seller Profile with Ratings](#seller-profile-with-ratings)
4. [Seller Reviews Tab](#seller-reviews-tab)
5. [Frontend Integration](#frontend-integration)
6. [Data Structure](#data-structure)

---

## Overview

Sellers can view:
- **Overall Rating**: Average star rating and total review count (displayed in profile)
- **Reviews/Comments**: All reviews/comments left by buyers (displayed in Reviews tab)
- **Rating Statistics**: Rating distribution (5-star, 4-star, etc.)

### Key Features:
- ✅ View all reviews/comments from buyers
- ✅ See average rating and total review count in profile
- ✅ View rating distribution (how many 5-star, 4-star, etc.)
- ✅ Pagination support for reviews list
- ✅ Review details include buyer info, product info, rating, and comment

---

## API Endpoints

### Base URL

```
https://dolabb-backend-2vsj.onrender.com
```

### Authentication

All endpoints require JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## API Endpoints

### 1. Get Seller Reviews/Comments

**Endpoint:** `GET /api/user/reviews/seller/<seller_id>/`

**Purpose:** Get all reviews/comments left by buyers for a specific seller. This shows all the comments buyers have written about the seller.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 20)

**Example Request:**
```javascript
GET /api/user/reviews/seller/507f1f77bcf86cd799439011/?page=1&limit=20
```

**Response (200 OK):**
```json
{
  "success": true,
  "reviews": [
    {
      "id": "review_id_1",
      "orderId": "order_id_1",
      "orderNumber": "ORD-12345",
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "fullName": "John Doe",
        "profileImage": "https://example.com/profile.jpg"
      },
      "product": {
        "id": "product_id",
        "title": "Vintage Denim Jacket",
        "image": "https://example.com/product-image.jpg"
      },
      "rating": 5,
      "comment": "Great seller! Fast shipping and product exactly as described. Highly recommend!",
      "createdAt": "2024-01-15T10:30:00Z"
    },
    {
      "id": "review_id_2",
      "orderId": "order_id_2",
      "orderNumber": "ORD-12346",
      "buyer": {
        "id": "buyer_id_2",
        "username": "buyer_username_2",
        "fullName": "Jane Smith",
        "profileImage": "https://example.com/profile2.jpg"
      },
      "product": {
        "id": "product_id_2",
        "title": "Leather Handbag",
        "image": "https://example.com/product-image2.jpg"
      },
      "rating": 4,
      "comment": "Good quality product. Shipping was a bit slow but seller was responsive.",
      "createdAt": "2024-01-14T08:20:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalItems": 25
  }
}
```

**Key Fields:**
- `id`: Review ID
- `orderId`: Order ID associated with the review
- `orderNumber`: Human-readable order number
- `buyer`: Buyer information (id, username, fullName, profileImage)
- `product`: Product information (id, title, image)
- `rating`: Star rating (1-5)
- `comment`: Review comment/feedback
- `createdAt`: When the review was created

---

### 2. Get Seller Rating Statistics

**Endpoint:** `GET /api/user/reviews/seller/<seller_id>/rating/`

**Purpose:** Get overall rating statistics for a seller including average rating, total reviews, and rating distribution.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "rating": {
    "averageRating": 4.5,
    "totalReviews": 25,
    "ratingDistribution": {
      "5": 15,
      "4": 7,
      "3": 2,
      "2": 1,
      "1": 0
    }
  }
}
```

**Key Fields:**
- `averageRating`: Average star rating (0-5, rounded to 2 decimals)
- `totalReviews`: Total number of reviews received
- `ratingDistribution`: Count of reviews by star rating (5-star, 4-star, etc.)

**Example with No Reviews:**
```json
{
  "success": true,
  "rating": {
    "averageRating": 0,
    "totalReviews": 0,
    "ratingDistribution": {
      "5": 0,
      "4": 0,
      "3": 0,
      "2": 0,
      "1": 0
    }
  }
}
```

---

### 3. Get Seller Profile (with Ratings)

**Endpoint:** `GET /api/auth/profile/`

**Purpose:** Get seller profile information including rating and review count.

**Headers:**
```
Authorization: Bearer <token>
```

**Response for Seller (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "seller_id",
    "username": "seller_username",
    "email": "seller@example.com",
    "phone": "+1234567890",
    "full_name": "Seller Name",
    "profile_image": "https://example.com/profile.jpg",
    "bio": "Professional seller with 5 years experience",
    "location": "Riyadh, Saudi Arabia",
    "shipping_address": "123 Main St",
    "zip_code": "12345",
    "house_number": "Apt 4B",
    "joined_date": "2023-01-15T10:00:00Z",
    "role": "seller",
    "rating": {
      "averageRating": 4.5,
      "totalReviews": 25,
      "ratingDistribution": {
        "5": 15,
        "4": 7,
        "3": 2,
        "2": 1,
        "1": 0
      }
    }
  }
}
```

**Note:** The `rating` field is only included when `role` is `"seller"`. For buyers, this field is not included.

---

## Seller Profile with Ratings

### Display in Profile Header

The seller profile should display:

1. **Average Rating** (e.g., "4.5 ⭐")
2. **Total Reviews Count** (e.g., "25 reviews")
3. **Star Display** (visual representation of rating)

**Example UI:**
```
┌─────────────────────────────────┐
│  [Profile Image]                │
│  Seller Name                    │
│  ⭐⭐⭐⭐⭐ 4.5 (25 reviews)    │
│  Location: Riyadh, Saudi Arabia │
└─────────────────────────────────┘
```

---

## Seller Reviews Tab

### Reviews Tab Structure

The Reviews tab should display:

1. **Summary Section:**
   - Average rating with stars
   - Total reviews count
   - Rating distribution chart/bar

2. **Reviews List:**
   - Each review card showing:
     - Buyer profile image and name
     - Product image and title
     - Star rating
     - Comment text
     - Review date
     - Order number (optional)

3. **Pagination:**
   - Load more / Next page button
   - Page numbers

**Example Review Card:**
```
┌─────────────────────────────────────┐
│ [Buyer Image] Buyer Name            │
│ ⭐⭐⭐⭐⭐ 5 stars                    │
│                                     │
│ "Great seller! Fast shipping..."   │
│                                     │
│ Product: Vintage Denim Jacket      │
│ [Product Image]                     │
│                                     │
│ Order: ORD-12345                   │
│ Date: Jan 15, 2024                 │
└─────────────────────────────────────┘
```

---

## Frontend Integration

### 1. Update TypeScript Types

**File:** `types/seller.ts` or `types/api.ts`

```typescript
export interface SellerReview {
  id: string;
  orderId: string;
  orderNumber: string;
  buyer: {
    id: string;
    username: string;
    fullName: string;
    profileImage?: string;
  };
  product: {
    id: string;
    title: string;
    image?: string;
  };
  rating: number; // 1-5
  comment: string;
  createdAt: string;
}

export interface SellerRating {
  averageRating: number;
  totalReviews: number;
  ratingDistribution: {
    '5': number;
    '4': number;
    '3': number;
    '2': number;
    '1': number;
  };
}

export interface SellerProfile {
  id: string;
  username: string;
  email: string;
  phone: string;
  full_name: string;
  profile_image?: string;
  bio?: string;
  location?: string;
  role: 'seller' | 'buyer';
  rating?: SellerRating; // Only for sellers
  // ... other fields
}
```

---

### 2. API Functions

**File:** `api/sellerApi.ts` or `api/reviewsApi.ts`

```typescript
import api from '../utils/api';

// Get seller reviews/comments
export const getSellerReviews = async (sellerId: string, params = {}) => {
  const { page = 1, limit = 20 } = params;
  const queryParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  
  const response = await api.get(
    `/api/user/reviews/seller/${sellerId}/?${queryParams}`
  );
  return response.data;
};

// Get seller rating statistics
export const getSellerRating = async (sellerId: string) => {
  const response = await api.get(`/api/user/reviews/seller/${sellerId}/rating/`);
  return response.data;
};
```

---

### 3. React Query Hooks

**File:** `hooks/useSellerReviews.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { getSellerReviews, getSellerRating } from '../api/sellerApi';

// Get seller reviews
export const useSellerReviews = (sellerId: string, params = {}) => {
  return useQuery({
    queryKey: ['sellerReviews', sellerId, params],
    queryFn: () => getSellerReviews(sellerId, params),
    enabled: !!sellerId,
  });
};

// Get seller rating
export const useSellerRating = (sellerId: string) => {
  return useQuery({
    queryKey: ['sellerRating', sellerId],
    queryFn: () => getSellerRating(sellerId),
    enabled: !!sellerId,
  });
};
```

---

### 4. Seller Profile Component

**File:** `components/profile/SellerProfile.tsx`

```tsx
import React from 'react';
import { useProfile } from '../hooks/useAuth';

const SellerProfile = () => {
  const { data: profileData } = useProfile();
  const user = profileData?.user;
  const rating = user?.rating;

  if (!user || user.role !== 'seller') {
    return <div>Not a seller</div>;
  }

  return (
    <div className="seller-profile">
      <div className="profile-header">
        <img
          src={user.profile_image || '/default-avatar.png'}
          alt={user.full_name}
          className="profile-image"
        />
        <div>
          <h1>{user.full_name}</h1>
          <p>{user.location}</p>
          
          {/* Rating Display */}
          {rating && rating.totalReviews > 0 ? (
            <div className="rating-display">
              <div className="stars">
                {Array.from({ length: 5 }).map((_, i) => (
                  <span
                    key={i}
                    className={i < Math.round(rating.averageRating) ? 'star filled' : 'star'}
                  >
                    ⭐
                  </span>
                ))}
              </div>
              <span className="rating-text">
                {rating.averageRating.toFixed(1)} ({rating.totalReviews} reviews)
              </span>
            </div>
          ) : (
            <div className="no-reviews">
              <span>No reviews yet</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="profile-bio">
        <p>{user.bio || 'No bio available'}</p>
      </div>
    </div>
  );
};

export default SellerProfile;
```

---

### 5. Seller Reviews Tab Component

**File:** `components/dashboard/ReviewsTab.tsx`

```tsx
import React, { useState } from 'react';
import { useSellerReviews, useSellerRating } from '../../hooks/useSellerReviews';
import { useProfile } from '../../hooks/useAuth';

const ReviewsTab = () => {
  const { data: profileData } = useProfile();
  const sellerId = profileData?.user?.id;
  
  const [page, setPage] = useState(1);
  const { data: reviewsData, isLoading: reviewsLoading } = useSellerReviews(
    sellerId,
    { page, limit: 10 }
  );
  const { data: ratingData, isLoading: ratingLoading } = useSellerRating(sellerId);
  
  const reviews = reviewsData?.reviews || [];
  const rating = ratingData?.rating || profileData?.user?.rating;
  const pagination = reviewsData?.pagination;
  
  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <span
        key={i}
        className={i < rating ? 'star filled' : 'star empty'}
      >
        ⭐
      </span>
    ));
  };
  
  if (reviewsLoading || ratingLoading) {
    return <div>Loading reviews...</div>;
  }
  
  return (
    <div className="reviews-tab">
      <h2>Reviews & Comments</h2>
      
      {/* Rating Summary */}
      {rating && rating.totalReviews > 0 && (
        <div className="rating-summary">
          <div className="average-rating">
            <h3>{rating.averageRating.toFixed(1)}</h3>
            <div className="stars">
              {renderStars(Math.round(rating.averageRating))}
            </div>
            <p>{rating.totalReviews} reviews</p>
          </div>
          
          {/* Rating Distribution */}
          <div className="rating-distribution">
            <h4>Rating Distribution</h4>
            {[5, 4, 3, 2, 1].map(star => (
              <div key={star} className="distribution-row">
                <span>{star} ⭐</span>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${(rating.ratingDistribution[star] / rating.totalReviews) * 100}%`
                    }}
                  />
                </div>
                <span>{rating.ratingDistribution[star]}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Reviews List */}
      <div className="reviews-list">
        {reviews.length === 0 ? (
          <div className="no-reviews">
            <p>No reviews yet. Reviews will appear here once buyers leave feedback.</p>
          </div>
        ) : (
          reviews.map(review => (
            <div key={review.id} className="review-card">
              <div className="review-header">
                <img
                  src={review.buyer.profileImage || '/default-avatar.png'}
                  alt={review.buyer.fullName}
                  className="buyer-avatar"
                />
                <div>
                  <h4>{review.buyer.fullName || review.buyer.username}</h4>
                  <p className="review-date">
                    {new Date(review.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="review-rating">
                {renderStars(review.rating)}
              </div>
              
              <p className="review-comment">{review.comment}</p>
              
              <div className="review-product">
                <img
                  src={review.product.image || '/default-product.png'}
                  alt={review.product.title}
                  className="product-thumbnail"
                />
                <div>
                  <p className="product-title">{review.product.title}</p>
                  <p className="order-number">Order: {review.orderNumber}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Pagination */}
      {pagination && pagination.totalPages > 1 && (
        <div className="pagination">
          <button
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </button>
          <span>
            Page {pagination.currentPage} of {pagination.totalPages}
          </span>
          <button
            disabled={page >= pagination.totalPages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewsTab;
```

---

## Data Structure

### Review Object Structure

```typescript
interface SellerReview {
  id: string;                    // Review ID
  orderId: string;               // Associated order ID
  orderNumber: string;           // Human-readable order number
  buyer: {
    id: string;                  // Buyer user ID
    username: string;            // Buyer username
    fullName: string;            // Buyer full name
    profileImage?: string;       // Buyer profile image URL
  };
  product: {
    id: string;                  // Product ID
    title: string;              // Product title
    image?: string;             // Product image URL
  };
  rating: number;               // Star rating (1-5)
  comment: string;              // Review comment/feedback
  createdAt: string;            // ISO date string
}
```

### Rating Statistics Structure

```typescript
interface SellerRating {
  averageRating: number;        // Average rating (0-5, 2 decimals)
  totalReviews: number;         // Total number of reviews
  ratingDistribution: {
    '5': number;                // Count of 5-star reviews
    '4': number;                // Count of 4-star reviews
    '3': number;                // Count of 3-star reviews
    '2': number;                // Count of 2-star reviews
    '1': number;                // Count of 1-star reviews
  };
}
```

---

## UI/UX Recommendations

### 1. Star Rating Display

**Visual Representation:**
- Use filled/empty stars: ⭐⭐⭐⭐⭐
- Show decimal rating: "4.5"
- Display total count: "(25 reviews)"

### 2. Review Cards

**Layout:**
- Buyer avatar and name at top
- Star rating prominently displayed
- Comment text in readable font
- Product thumbnail and title
- Order number (optional, smaller text)
- Review date

### 3. Rating Distribution

**Visualization:**
- Progress bars showing percentage
- Count next to each star level
- Color coding (green for 5-star, yellow for 3-star, red for 1-star)

### 4. Empty States

**No Reviews:**
- Friendly message: "No reviews yet. Reviews will appear here once buyers leave feedback."
- Encourage sellers to provide good service

---

## Testing

### Test Get Seller Reviews

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/user/reviews/seller/SELLER_ID/?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Get Seller Rating

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/user/reviews/seller/SELLER_ID/rating/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Get Profile (with Ratings)

```bash
curl -X GET "https://dolabb-backend-2vsj.onrender.com/api/auth/profile/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Summary

**Seller Reviews APIs:**
- `GET /api/user/reviews/seller/<seller_id>/` - Get all reviews/comments
- `GET /api/user/reviews/seller/<seller_id>/rating/` - Get rating statistics
- `GET /api/auth/profile/` - Get profile with rating (for sellers)

**Key Features:**
- ✅ View all buyer reviews/comments
- ✅ See average rating and total reviews in profile
- ✅ View rating distribution
- ✅ Pagination support
- ✅ Review details with buyer and product info

**Frontend Components:**
- `SellerProfile` - Display rating in profile header
- `ReviewsTab` - Display all reviews with summary
- Rating display components
- Review cards with buyer/product info

---

**Last Updated:** 2024-01-15
**Backend Version:** v1.2.0 (with seller reviews & ratings)

