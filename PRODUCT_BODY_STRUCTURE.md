# Product Create/Update Body Structure

This document describes the complete body structure for creating and updating
products. Both create and update endpoints use the same field structure, but
with different requirements.

## Important: Create vs Update

- **CREATE Product**: Requires `itemtitle`, `price`, and `category`. All other
  fields are optional.
- **UPDATE Product**: **ALL fields are optional**. You can send an empty body
  `{}` or only the fields you want to update (partial updates).

## Complete Body Structure

```json
{
  // REQUIRED FIELDS
  "itemtitle": "Vintage Denim Jacket", // Required: Product title
  "price": 100, // Required: Current selling price
  "category": "women", // Required: One of ['women', 'men', 'watches', 'jewelry', 'accessories']

  // OPTIONAL FIELDS
  "description": "Beautiful vintage denim jacket", // Optional: Product description
  "originalPrice": 120, // Optional: Original price before discount (defaults to price if not provided)
  "subcategory": "", // Optional: Product subcategory
  "brand": "", // Optional: Product brand name
  "currency": "SAR", // Optional: Currency code (defaults to 'SAR')
  "Quantity": 10, // Optional: Available quantity (defaults to 1)
  "gender": "", // Optional: Gender specification
  "Size": "M", // Optional: Product size
  "Color": "", // Optional: Product color
  "Condition": "good", // Optional: One of ['new', 'like-new', 'good', 'fair'] (defaults to 'good')
  "SKU/ID (Optional)": "", // Optional: SKU or product ID
  "Tags/Keywords": ["vintage", "denim", "jacket"], // Optional: Array of tags/keywords
  "Images": ["url1", "url2"], // Optional: Array of image URLs
  "Shipping Cost": 10, // Optional: Shipping cost (defaults to 0.0)
  "Processing Time (days)": 3, // Optional: Processing time in days (defaults to 7)
  "Shipping Locations": [], // Optional: Array of shipping location strings
  "Affiliate Code (Optional)": "" // Optional: Affiliate code for tracking
}
```

## Field Details

### Required Fields (CREATE ONLY)

**Note**: These fields are ONLY required when **creating** a product. When
**updating**, ALL fields are optional.

- **itemtitle** (string): Product title, max 500 characters
- **price** (number): Current selling price, must be a positive number
- **category** (string): Must be one of: `'women'`, `'men'`, `'watches'`,
  `'jewelry'`, `'accessories'`

### Optional Fields with Defaults

- **originalPrice** (number): If not provided, defaults to `price`
- **currency** (string): If not provided, defaults to `'SAR'`
- **Quantity** (number): If not provided, defaults to `1`
- **Condition** (string): If not provided, defaults to `'good'`
- **Shipping Cost** (number): If not provided, defaults to `0.0`
- **Processing Time (days)** (number): If not provided, defaults to `7`

### Optional Fields (Empty by Default)

- **description** (string): Product description
- **subcategory** (string): Product subcategory
- **brand** (string): Product brand name
- **gender** (string): Gender specification
- **Size** (string): Product size
- **Color** (string): Product color
- **SKU/ID (Optional)** (string): SKU or product identifier
- **Tags/Keywords** (array): Array of tag strings
- **Images** (array): Array of image URL strings
- **Shipping Locations** (array): Array of location strings
- **Affiliate Code (Optional)** (string): Affiliate tracking code

## Notes

1. **Images Field**:

   - When creating: Provide array of image URLs
   - When updating: Provide complete array (will replace existing images)

2. **Empty Strings vs Omitted Fields**:

   - Empty strings (`""`) are accepted for optional text fields
   - Omitting a field entirely uses the default value (if applicable)

3. **Arrays**:

   - Empty arrays (`[]`) are accepted for array fields
   - If omitted, defaults to empty array

4. **Create vs Update**:
   - **CREATE**: Requires `itemtitle`, `price`, and `category`. All other fields
     are optional.
   - **UPDATE**: **ALL fields are optional**. Send only the fields you want to
     change. You can even send an empty body `{}` (will just update the
     `updated_at` timestamp).
   - Both use the same field names and structure

## Example: Minimal Required Body (CREATE)

```json
{
  "itemtitle": "Product Name",
  "price": 50,
  "category": "women"
}
```

## Example: Partial Update (UPDATE)

You can update just one field, multiple fields, or send an empty body:

```json
// Update only price
{
  "price": 75
}
```

```json
// Update multiple fields
{
  "price": 75,
  "Quantity": 5,
  "description": "Updated description"
}
```

```json
// Empty body (just updates timestamp)
{}
```

## Example: Complete Body

```json
{
  "itemtitle": "Vintage Denim Jacket",
  "description": "Beautiful vintage denim jacket in excellent condition",
  "price": 100,
  "originalPrice": 120,
  "category": "women",
  "subcategory": "Jackets",
  "brand": "Levi's",
  "currency": "SAR",
  "Quantity": 10,
  "gender": "Unisex",
  "Size": "M",
  "Color": "Blue",
  "Condition": "good",
  "SKU/ID (Optional)": "LEV-DEN-001",
  "Tags/Keywords": ["vintage", "denim", "jacket", "casual"],
  "Images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "Shipping Cost": 10,
  "Processing Time (days)": 3,
  "Shipping Locations": ["Saudi Arabia", "UAE", "Kuwait"],
  "Affiliate Code (Optional)": "AFF123"
}
```
