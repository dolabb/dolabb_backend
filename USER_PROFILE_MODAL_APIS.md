# User Profile Modal APIs

This document lists all the APIs available for displaying user profile information, products, and reviews in a modal.

## Overview

When clicking on a user's profile (in messages or product detail page), you can use these APIs to display:
- User profile information
- User's listed products
- User's reviews and ratings

## Available APIs

### 1. Get User Profile by User ID
**Endpoint:** `GET /api/auth/profile/<user_id>/`  
**Authentication:** Not required (public endpoint)  
**Description:** Get user profile information including basic details and seller rating stats (if seller)

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "user_id",
    "username": "username",
    "email": "email@example.com",
    "phone": "phone_number",
    "full_name": "Full Name",
    "profile_image": "image_url",
    "bio": "Bio text",
    "location": "Location",
    "role": "seller" | "buyer",
    "joined_date": "2024-01-01T00:00:00Z",
    "rating": {
      "averageRating": 4.5,
      "totalReviews": 10,
      "ratingDistribution": {
        "5": 5,
        "4": 3,
        "3": 1,
        "2": 1,
        "1": 0
      }
    }
  }
}
```

**Note:** The `rating` field is only included if the user is a seller.

---

### 2. Get Products by Seller ID
**Endpoint:** `GET /api/user/seller/<seller_id>/products/`  
**Authentication:** Not required (public endpoint)  
**Description:** Get all products listed by a specific seller

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by product status (e.g., "active", "sold")

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": "product_id",
      "title": "Product Title",
      "description": "Product description",
      "price": 100.00,
      "originalPrice": 120.00,
      "currency": "SAR",
      "images": ["image1.jpg", "image2.jpg"],
      "category": "Category",
      "subcategory": "Subcategory",
      "brand": "Brand",
      "size": "Size",
      "color": "Color",
      "condition": "new",
      "status": "active",
      "approved": true,
      "quantity": 1,
      "isSaved": false,
      "seller": {
        "id": "seller_id",
        "username": "seller_username",
        "fullName": "Seller Name",
        "profileImage": "profile_image_url",
        "rating": 4.5
      },
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 100
  }
}
```

**Note:** The `isSaved` field indicates if the product is saved in the authenticated user's wishlist (only if user is logged in).

---

### 3. Get Seller Reviews
**Endpoint:** `GET /api/user/reviews/seller/<seller_id>/`  
**Authentication:** Not required (public endpoint)  
**Description:** Get all reviews/comments for a specific seller

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "reviews": [
    {
      "id": "review_id",
      "orderId": "order_id",
      "orderNumber": "ORD123456",
      "buyer": {
        "id": "buyer_id",
        "username": "buyer_username",
        "fullName": "Buyer Name",
        "profileImage": "profile_image_url"
      },
      "product": {
        "id": "product_id",
        "title": "Product Title",
        "image": "product_image.jpg"
      },
      "rating": 5,
      "comment": "Great product!",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalItems": 25
  }
}
```

---

### 4. Get Seller Rating Statistics
**Endpoint:** `GET /api/user/reviews/seller/<seller_id>/rating/`  
**Authentication:** Not required (public endpoint)  
**Description:** Get seller rating statistics (average rating, total reviews, rating distribution)

**Response:**
```json
{
  "success": true,
  "rating": {
    "average_rating": 4.5,
    "total_reviews": 10,
    "rating_distribution": {
      "5": 5,
      "4": 3,
      "3": 1,
      "2": 1,
      "1": 0
    }
  }
}
```

---

## Usage Example

### Frontend Implementation Flow

1. **User clicks on profile** (in messages or product detail page)
   - Extract `user_id` or `seller_id` from the context

2. **Fetch user profile:**
   ```javascript
   GET /api/auth/profile/{user_id}/
   ```

3. **Fetch user's products:**
   ```javascript
   GET /api/user/seller/{seller_id}/products/?page=1&limit=10
   ```

4. **Fetch user's reviews:**
   ```javascript
   GET /api/user/reviews/seller/{seller_id}/?page=1&limit=10
   ```

5. **Display in modal:**
   - Show user profile information
   - Show products list
   - Show reviews list
   - Show rating statistics

### Example API Calls

```javascript
// Get user profile
const profileResponse = await fetch(`/api/auth/profile/${userId}/`);
const profileData = await profileResponse.json();

// Get user's products
const productsResponse = await fetch(`/api/user/seller/${userId}/products/?page=1&limit=10`);
const productsData = await productsResponse.json();

// Get user's reviews
const reviewsResponse = await fetch(`/api/user/reviews/seller/${userId}/?page=1&limit=10`);
const reviewsData = await reviewsResponse.json();

// Get seller rating stats
const ratingResponse = await fetch(`/api/user/reviews/seller/${userId}/rating/`);
const ratingData = await ratingResponse.json();
```

---

## Notes

- All endpoints are **public** (no authentication required), but some fields (like `isSaved`) will only be populated if the user is authenticated
- For sellers, the rating information is included in the profile response
- Products endpoint supports pagination
- Reviews endpoint supports pagination
- All endpoints return proper error responses with `success: false` and `error` message on failure

---

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

Common HTTP status codes:
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (user/product not found)
- `500`: Internal Server Error

