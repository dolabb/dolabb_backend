# Frontend Changes for Out of Stock Products

## Overview
The backend has been updated to handle out-of-stock products differently. Products with quantity 0 or less will now remain visible in the seller's product list with an "out of stock" status, allowing sellers to easily restock them.

## Backend Changes Summary

### 1. New Field: `isOutOfStock`
All product list endpoints for sellers now include an `isOutOfStock` boolean field that indicates whether a product is out of stock (quantity <= 0).

### 2. Product Status Behavior
- Products with quantity 0 are marked with status `'sold'` but remain visible to sellers
- When a seller updates a product's quantity from 0 to a positive number, the status automatically changes back to `'active'`
- Public product listings still filter out products with status `'sold'` (out of stock products won't appear in public searches)

## Frontend Implementation Guide

### 1. Update Product List Display for Sellers

#### Endpoints Affected:
- `GET /api/products/seller/` - Get seller's own products
- `GET /api/products/user/products/` - Get user's products (alternative endpoint)

#### Response Structure:
```json
{
  "id": "product_id",
  "title": "Product Title",
  "quantity": 0,
  "isOutOfStock": true,
  "status": "sold",
  // ... other fields
}
```

#### Implementation Steps:

1. **Display Out of Stock Badge/Indicator**
   - Add a visual indicator (badge, label, or icon) when `isOutOfStock === true`
   - Suggested UI elements:
     - Red "Out of Stock" badge
     - Gray overlay on product image
     - Warning icon next to product title
     - Disabled state styling

2. **Product Card Component Example (React/TypeScript)**
   ```tsx
   interface Product {
     id: string;
     title: string;
     quantity: number;
     isOutOfStock: boolean;
     status: string;
     // ... other fields
   }

   const ProductCard = ({ product }: { product: Product }) => {
     return (
       <div className={`product-card ${product.isOutOfStock ? 'out-of-stock' : ''}`}>
         {product.isOutOfStock && (
           <span className="badge badge-out-of-stock">Out of Stock</span>
         )}
         <h3>{product.title}</h3>
         <p>Quantity: {product.quantity}</p>
         {/* Rest of product card */}
       </div>
     );
   };
   ```

3. **Product List View**
   - Show all products regardless of stock status
   - Sort or filter options:
     - Add a filter toggle: "Show out of stock" (default: true for sellers)
     - Consider grouping: "In Stock" and "Out of Stock" sections
     - Add visual distinction between in-stock and out-of-stock products

### 2. Update Product Edit/Update Form

#### Endpoint:
- `PUT /api/products/{product_id}/` - Update product

#### Implementation Steps:

1. **Allow Quantity Updates for Out of Stock Products**
   - Ensure the quantity input field is always editable, even when `isOutOfStock === true`
   - Remove any restrictions that prevent editing out-of-stock products
   - Show a helpful message: "Update quantity to restock this product"

2. **Update Form Example**
   ```tsx
   const ProductEditForm = ({ product }: { product: Product }) => {
     const [quantity, setQuantity] = useState(product.quantity);
     
     const handleSubmit = async () => {
       const response = await fetch(`/api/products/${product.id}/`, {
         method: 'PUT',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({
           Quantity: quantity,
           // ... other fields
         })
       });
       
       // After successful update, refresh product list
       // The product status will automatically change to 'active' if quantity > 0
     };
     
     return (
       <form onSubmit={handleSubmit}>
         <div className="form-group">
           <label>Quantity</label>
           <input
             type="number"
             min="0"
             value={quantity}
             onChange={(e) => setQuantity(parseInt(e.target.value))}
           />
           {product.isOutOfStock && (
             <p className="help-text">
               This product is out of stock. Increase quantity to make it available again.
             </p>
           )}
         </div>
         {/* Other form fields */}
       </form>
     );
   };
   ```

3. **Success Message**
   - When quantity is updated from 0 to a positive number, show a success message:
     - "Product restocked successfully! It is now available for purchase."

### 3. Product Detail View Updates

#### For Seller's Own Products:
- Display stock status prominently
- Show "Out of Stock" indicator if `isOutOfStock === true`
- Enable "Update Product" button even when out of stock
- Show current quantity clearly

#### Example:
```tsx
const ProductDetail = ({ product }: { product: Product }) => {
  return (
    <div className="product-detail">
      <h1>{product.title}</h1>
      
      {product.isOutOfStock ? (
        <div className="alert alert-warning">
          <strong>Out of Stock</strong>
          <p>This product is currently out of stock. Update the quantity to make it available again.</p>
          <button onClick={() => navigate(`/products/${product.id}/edit`)}>
            Update Stock
          </button>
        </div>
      ) : (
        <div className="stock-info">
          <p>In Stock: {product.quantity} available</p>
        </div>
      )}
      
      {/* Rest of product details */}
    </div>
  );
};
```

### 4. Filtering and Sorting Options

#### Recommended UI Enhancements:

1. **Filter Toggle**
   ```tsx
   const [showOutOfStock, setShowOutOfStock] = useState(true);
   
   // Filter products
   const filteredProducts = showOutOfStock 
     ? products 
     : products.filter(p => !p.isOutOfStock);
   ```

2. **Sort Options**
   - Add sorting by stock status: "In Stock First" or "Out of Stock First"
   - Consider grouping: "In Stock" section and "Out of Stock" section

3. **Search/Filter Bar**
   - Add a quick filter: "Show only out of stock" checkbox
   - Add a filter: "Show only in stock" checkbox

### 5. Visual Design Recommendations

#### Color Scheme:
- **Out of Stock**: Red (#dc3545) or Orange (#ffc107)
- **In Stock**: Green (#28a745)
- **Low Stock** (if quantity < 5): Yellow/Orange warning

#### Icons:
- Out of Stock: ⚠️ or 🚫 or custom icon
- In Stock: ✓ or ✅

#### CSS Example:
```css
.product-card.out-of-stock {
  opacity: 0.7;
  position: relative;
}

.product-card.out-of-stock::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

.badge-out-of-stock {
  background-color: #dc3545;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}
```

### 6. User Experience Flow

#### Scenario: Seller Restocking a Product

1. **Seller views product list**
   - Sees product with "Out of Stock" badge
   - Product is still visible in the list

2. **Seller clicks "Edit" on out-of-stock product**
   - Edit form opens normally
   - Quantity field shows current value (0)
   - Helpful message displayed

3. **Seller updates quantity to 10**
   - Submits form
   - Backend automatically changes status to 'active'
   - Product becomes available in public listings

4. **Seller sees updated product**
   - "Out of Stock" badge removed
   - Status shows as 'active'
   - Quantity shows as 10

### 7. Testing Checklist

- [ ] Out-of-stock products are visible in seller's product list
- [ ] "Out of Stock" indicator is displayed correctly
- [ ] Out-of-stock products can be edited
- [ ] Quantity can be updated for out-of-stock products
- [ ] After updating quantity from 0 to positive, product status changes to 'active'
- [ ] Out-of-stock products do NOT appear in public product listings
- [ ] Filtering works correctly (show/hide out of stock)
- [ ] Visual indicators are clear and accessible

### 8. API Response Examples

#### Seller Product List Response:
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "title": "Product Name",
    "quantity": 0,
    "isOutOfStock": true,
    "status": "sold",
    "price": 100.00,
    "currency": "SAR",
    "images": ["url1", "url2"],
    "category": "women",
    "approved": true,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-15T00:00:00Z"
  },
  {
    "id": "507f1f77bcf86cd799439012",
    "title": "Another Product",
    "quantity": 5,
    "isOutOfStock": false,
    "status": "active",
    "price": 200.00,
    "currency": "SAR",
    "images": ["url3"],
    "category": "men",
    "approved": true,
    "createdAt": "2024-01-02T00:00:00Z",
    "updatedAt": "2024-01-10T00:00:00Z"
  }
]
```

#### Update Product Request:
```json
PUT /api/products/{product_id}/
{
  "Quantity": 10,
  "itemtitle": "Product Name",
  "price": 100.00
  // ... other fields
}
```

#### Update Product Response (after restocking):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "itemtitle": "Product Name",
  "Quantity": 10,
  "status": "active",  // Changed from "sold" to "active"
  // ... other fields
}
```

## Notes

- The `isOutOfStock` field is calculated as: `quantity === null || quantity <= 0`
- Products with status `'sold'` are automatically changed to `'active'` when quantity is updated to a positive number
- Public product listings (for buyers) continue to filter out products with status `'sold'`
- Sellers can always see and manage all their products, regardless of stock status

## Questions or Issues?

If you encounter any issues implementing these changes or need clarification, please contact the backend team.

