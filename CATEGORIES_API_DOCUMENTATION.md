# Categories & Subcategories API Documentation

## Overview
This document outlines the API requirements for categories, subcategories, and product listings for **non-logged-in users** in the Dolabb marketplace. The API should support browsing products across five main categories: Women, Men, Watches, Jewellery, and Accessories, along with their respective subcategories.

---

## Table of Contents
1. [Category Structure](#category-structure)
2. [API Endpoints](#api-endpoints)
3. [Request/Response Formats](#requestresponse-formats)
4. [Filtering & Sorting](#filtering--sorting)
5. [Pagination](#pagination)
6. [Examples](#examples)

---

## Category Structure

### Main Categories
1. **Women** (`women`)
2. **Men** (`men`)
3. **Watches** (`watches`)
4. **Jewellery** (`jewellery`)
5. **Accessories** (`accessories`)

### Subcategories by Category

#### 1. Women (`women`)
- `tops` - Tops
- `shoes` - Shoes
- `jeans` - Jeans
- `bags-purses` - Bags & Purses
- `sweaters` - Sweaters
- `sunglasses` - Sunglasses
- `skirts` - Skirts
- `hats` - Hats
- `dresses` - Dresses
- `coats-jackets` - Coats & Jackets
- `plus-size` - Plus Size

**Featured Collections:**
- `wardrobe-essentials` - Wardrobe essentials
- `denim-everything` - Denim everything
- `lifestyle-sneakers` - Lifestyle sneakers
- `office-wear` - Office wear
- `gym-gear` - Gym gear

#### 2. Men (`men`)
- `tshirts` - T-shirts
- `shoes` - Shoes
- `shirts` - Shirts
- `bags` - Bags
- `hoodies` - Hoodies
- `hats` - Hats
- `jeans` - Jeans
- `sweaters` - Sweaters
- `sunglasses` - Sunglasses
- `coats-jackets` - Coats & Jackets
- `big-tall` - Big & Tall

**Featured Collections:**
- `wardrobe-essentials` - Wardrobe essentials
- `denim-everything` - Denim everything
- `lifestyle-sneakers` - Lifestyle sneakers
- `office-wear` - Office wear
- `gym-gear` - Gym gear

#### 3. Watches (`watches`)
- `mens-watches` - Men's Watches
- `womens-watches` - Women's Watches
- `smart-watches` - Smart Watches
- `luxury-watches` - Luxury Watches
- `sports-watches` - Sports Watches
- `vintage-watches` - Vintage Watches
- `dress-watches` - Dress Watches
- `casual-watches` - Casual Watches

**Featured Collections:**
- `best-sellers` - Best Sellers
- `new-arrivals` - New Arrivals
- `on-sale` - On Sale

#### 4. Jewellery (`jewellery`)
- `rings` - Rings
- `necklaces` - Necklaces
- `earrings` - Earrings
- `bracelets` - Bracelets
- `pendants` - Pendants
- `chains` - Chains
- `anklets` - Anklets
- `brooches` - Brooches
- `cufflinks` - Cufflinks

**Featured Collections:**
- `gold-collection` - Gold Collection
- `silver-collection` - Silver Collection
- `diamond-collection` - Diamond Collection
- `vintage-jewellery` - Vintage Jewellery

#### 5. Accessories (`accessories`)
- `bags` - Bags
- `belts` - Belts
- `hats-caps` - Hats & Caps
- `sunglasses` - Sunglasses
- `scarves` - Scarves
- `wallets` - Wallets
- `phone-cases` - Phone Cases
- `keychains` - Keychains
- `hair-accessories` - Hair Accessories
- `ties-bow-ties` - Ties & Bow Ties

**Featured Collections:**
- `designer-bags` - Designer Bags
- `luxury-accessories` - Luxury Accessories
- `trending-now` - Trending Now

---

## API Endpoints

### 1. Get All Categories
**Endpoint:** `GET /api/categories/`

**Description:** Retrieve all main categories with their subcategories and metadata.

**Authentication:** Not required (public endpoint)

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": "women",
      "name": "Women",
      "key": "women",
      "href": "/women",
      "subCategories": [
        {
          "id": "tops",
          "name": "Tops",
          "key": "tops",
          "href": "/women/tops"
        },
        {
          "id": "shoes",
          "name": "Shoes",
          "key": "shoes",
          "href": "/women/shoes"
        }
        // ... more subcategories
      ],
      "featured": [
        {
          "id": "wardrobe-essentials",
          "name": "Wardrobe essentials",
          "key": "wardrobe-essentials",
          "href": "/women/wardrobe-essentials"
        }
        // ... more featured items
      ]
    }
    // ... more categories
  ]
}
```

---

### 2. Get Category Details
**Endpoint:** `GET /api/categories/{category_key}/`

**Description:** Get detailed information about a specific category including all subcategories and featured collections.

**Authentication:** Not required

**Parameters:**
- `category_key` (path parameter): The category key (e.g., `women`, `men`, `watches`, `jewellery`, `accessories`)

**Response:**
```json
{
  "success": true,
  "category": {
    "id": "women",
    "name": "Women",
    "key": "women",
    "href": "/women",
    "subCategories": [
      {
        "id": "tops",
        "name": "Tops",
        "key": "tops",
        "href": "/women/tops",
        "productCount": 245
      }
      // ... more subcategories
    ],
    "featured": [
      {
        "id": "wardrobe-essentials",
        "name": "Wardrobe essentials",
        "key": "wardrobe-essentials",
        "href": "/women/wardrobe-essentials",
        "productCount": 89
      }
      // ... more featured items
    ],
    "totalProducts": 1523
  }
}
```

---

### 3. Get Products by Category
**Endpoint:** `GET /api/products/`

**Description:** Get products filtered by category and/or subcategory. Supports filtering, sorting, and pagination.

**Authentication:** Not required

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Main category key (e.g., `women`, `men`) |
| `subcategory` | string | No | Subcategory key (e.g., `tops`, `shoes`) |
| `brand` | string | No | Brand name filter (can be multiple, comma-separated) |
| `minPrice` | number | No | Minimum price filter |
| `maxPrice` | number | No | Maximum price filter |
| `size` | string | No | Size filter (can be multiple, comma-separated) |
| `color` | string | No | Color filter (can be multiple, comma-separated) |
| `condition` | string | No | Condition filter: `new`, `like-new`, `good`, `fair` |
| `onSale` | boolean | No | Filter for products on sale only |
| `sortBy` | string | No | Sort option: `relevance`, `newest`, `price-low`, `price-high` |
| `page` | number | No | Page number (default: 1) |
| `limit` | number | No | Items per page (default: 20, max: 100) |
| `search` | string | No | Search query for product title/description |

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": "prod-123",
      "title": "Vintage Denim Jacket",
      "description": "Classic vintage denim jacket in excellent condition...",
      "price": 89.99,
      "originalPrice": 120.00,
      "images": [
        "https://www.dolabb.com/media/uploads/products/image1.jpg",
        "https://www.dolabb.com/media/uploads/products/image2.jpg"
      ],
      "category": "women",
      "subcategory": "coats-jackets",
      "brand": "Levi's",
      "size": "M",
      "color": "Blue",
      "condition": "like-new",
      "tags": ["vintage", "denim", "jacket"],
      "seller": {
        "id": "seller-456",
        "username": "fashion_lover",
        "profileImage": "https://www.dolabb.com/media/uploads/profiles/profile.jpg",
        "rating": 4.8,
        "totalSales": 156
      },
      "isSaved": false,
      "isLiked": false,
      "likes": 23,
      "shippingInfo": {
        "cost": 15.00,
        "estimatedDays": 3,
        "locations": ["Saudi Arabia", "UAE"]
      },
      "status": "active",
      "quantity": 1,
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-20T14:22:00Z"
    }
    // ... more products
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 15,
    "totalItems": 289,
    "itemsPerPage": 20,
    "hasNextPage": true,
    "hasPreviousPage": false
  },
  "filters": {
    "availableBrands": ["Levi's", "Nike", "Adidas", "Zara"],
    "availableSizes": ["XS", "S", "M", "L", "XL"],
    "availableColors": ["Blue", "Black", "White", "Red"],
    "priceRange": {
      "min": 10.00,
      "max": 500.00
    }
  }
}
```

---

### 4. Get Filter Options for Category
**Endpoint:** `GET /api/categories/{category_key}/filters/`

**Description:** Get available filter options (brands, sizes, colors, price range) for a specific category/subcategory.

**Authentication:** Not required

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subcategory` | string | No | Filter by subcategory to get relevant options |

**Response:**
```json
{
  "success": true,
  "filters": {
    "brands": [
      {
        "name": "Levi's",
        "count": 45
      },
      {
        "name": "Nike",
        "count": 32
      }
      // ... more brands
    ],
    "sizes": [
      {
        "name": "XS",
        "count": 12
      },
      {
        "name": "S",
        "count": 89
      }
      // ... more sizes
    ],
    "colors": [
      {
        "name": "Blue",
        "count": 156
      },
      {
        "name": "Black",
        "count": 203
      }
      // ... more colors
    ],
    "conditions": [
      {
        "name": "new",
        "count": 45
      },
      {
        "name": "like-new",
        "count": 123
      }
      // ... more conditions
    ],
    "priceRange": {
      "min": 10.00,
      "max": 500.00
    }
  }
}
```

---

## Request/Response Formats

### Product Object Structure
```typescript
interface Product {
  id: string;                    // Unique product identifier
  title: string;                  // Product title
  description: string;            // Product description
  price: number;                  // Current price
  originalPrice?: number;         // Original price (if on sale)
  images: string[];               // Array of image URLs
  category: string;                // Main category key
  subcategory?: string;            // Subcategory key
  brand?: string;                  // Brand name
  size?: string;                   // Size (e.g., "M", "L", "42")
  color?: string;                 // Color name
  condition: 'new' | 'like-new' | 'good' | 'fair';
  tags?: string[];                // Product tags
  seller: {
    id: string;
    username: string;
    profileImage?: string;
    rating?: number;              // Average rating (0-5)
    totalSales?: number;          // Total number of sales
  };
  isSaved?: boolean;              // Whether product is saved (requires auth)
  isLiked?: boolean;              // Whether product is liked (requires auth)
  likes?: number;                 // Total number of likes
  shippingInfo?: {
    cost: number;
    estimatedDays: number;
    locations: string[];
  };
  status: 'pending' | 'approved' | 'rejected' | 'active' | 'sold';
  quantity?: number;              // Available quantity
  createdAt?: string;             // ISO 8601 date string
  updatedAt?: string;             // ISO 8601 date string
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**Common Error Codes:**
- `INVALID_CATEGORY` - Category not found
- `INVALID_SUBCATEGORY` - Subcategory not found
- `INVALID_FILTER` - Invalid filter parameter
- `INVALID_PAGINATION` - Invalid page or limit parameter
- `SERVER_ERROR` - Internal server error

---

## Filtering & Sorting

### Filter Options

#### Category Filter
- Filter by main category: `category=women`
- Filter by subcategory: `subcategory=tops`
- Combine both: `category=women&subcategory=tops`

#### Brand Filter
- Single brand: `brand=Levi's`
- Multiple brands: `brand=Levi's,Nike,Adidas`

#### Price Filter
- Minimum price: `minPrice=50`
- Maximum price: `maxPrice=200`
- Price range: `minPrice=50&maxPrice=200`

#### Size Filter
- Single size: `size=M`
- Multiple sizes: `size=M,L,XL`

#### Color Filter
- Single color: `color=Blue`
- Multiple colors: `color=Blue,Black,Red`

#### Condition Filter
- Options: `new`, `like-new`, `good`, `fair`
- Example: `condition=like-new`

#### Sale Filter
- On sale only: `onSale=true`

#### Search Filter
- Search in title/description: `search=denim jacket`

### Sorting Options

| Value | Description |
|-------|-------------|
| `relevance` | Default sorting (relevance-based) |
| `newest` | Sort by creation date (newest first) |
| `price-low` | Sort by price (low to high) |
| `price-high` | Sort by price (high to low) |

---

## Pagination

### Pagination Parameters
- `page`: Page number (starts from 1)
- `limit`: Number of items per page (default: 20, max: 100)

### Pagination Response
```json
{
  "pagination": {
    "currentPage": 1,
    "totalPages": 15,
    "totalItems": 289,
    "itemsPerPage": 20,
    "hasNextPage": true,
    "hasPreviousPage": false
  }
}
```

---

## Examples

### Example 1: Get All Women's Products
**Request:**
```
GET /api/products/?category=women&page=1&limit=20
```

**Response:** Returns first 20 products from the Women category.

---

### Example 2: Get Women's Tops with Filters
**Request:**
```
GET /api/products/?category=women&subcategory=tops&brand=Zara&size=M&minPrice=30&maxPrice=100&sortBy=price-low
```

**Response:** Returns Zara tops in size M, priced between 30-100 SAR, sorted by price (low to high).

---

### Example 3: Get Watches - Men's Luxury Watches
**Request:**
```
GET /api/products/?category=watches&subcategory=mens-watches&condition=new&sortBy=price-high&limit=12
```

**Response:** Returns 12 new men's luxury watches, sorted by price (high to low).

---

### Example 4: Get Jewellery - Gold Collection
**Request:**
```
GET /api/products/?category=jewellery&subcategory=rings&search=gold&onSale=true
```

**Response:** Returns gold rings that are currently on sale.

---

### Example 5: Get Accessories with Multiple Filters
**Request:**
```
GET /api/products/?category=accessories&subcategory=bags&brand=Gucci,Prada&color=Black,Brown&minPrice=200&maxPrice=1000&condition=like-new&sortBy=newest&page=2&limit=24
```

**Response:** Returns page 2 of Gucci and Prada bags in black or brown, priced 200-1000 SAR, in like-new condition, sorted by newest.

---

### Example 6: Get Category Filter Options
**Request:**
```
GET /api/categories/women/filters/?subcategory=tops
```

**Response:** Returns available brands, sizes, colors, and price range for Women's Tops category.

---

## Important Notes

1. **No Authentication Required**: All endpoints listed above should be accessible to non-logged-in users.

2. **Image URLs**: All product images should be publicly accessible URLs. The API should return full URLs, not relative paths.

3. **Seller Information**: For non-logged-in users, seller information should be limited to:
   - Username
   - Profile image
   - Rating
   - Total sales
   - **NOT** included: Email, phone, address, or other sensitive information

4. **Product Status**: Only products with status `active` should be returned to non-logged-in users.

5. **Price Format**: All prices should be in SAR (Saudi Riyal) and formatted as numbers with 2 decimal places.

6. **Date Format**: All dates should be in ISO 8601 format (e.g., `2024-01-15T10:30:00Z`).

7. **Localization**: The API should support locale parameters for multi-language support (English/Arabic):
   - Add `?locale=en` or `?locale=ar` query parameter
   - Return localized category/subcategory names based on locale

8. **Performance**: 
   - Implement caching for category/subcategory lists
   - Use pagination to limit response sizes
   - Consider implementing search indexing for better search performance

9. **Rate Limiting**: Implement appropriate rate limiting to prevent abuse while allowing normal browsing.

10. **CORS**: Ensure CORS headers are properly configured to allow frontend access.

---

## Additional Recommendations

### Search Functionality
Consider implementing a dedicated search endpoint:
```
GET /api/search/?q=denim&category=women&page=1&limit=20
```

### Featured Products
Consider an endpoint for featured products by category:
```
GET /api/categories/women/featured/
```

### Related Products
When viewing a product, consider including related products:
```
GET /api/products/{product_id}/related/
```

---

## Summary

This API documentation covers:
- ✅ 5 main categories (Women, Men, Watches, Jewellery, Accessories)
- ✅ All subcategories for each main category
- ✅ Featured collections for each category
- ✅ Product listing with filtering, sorting, and pagination
- ✅ Filter options endpoint
- ✅ Public access (no authentication required)
- ✅ Complete product information structure
- ✅ Error handling
- ✅ Localization support

The API should be RESTful, well-documented, and optimized for performance to support a smooth browsing experience for non-logged-in users.

