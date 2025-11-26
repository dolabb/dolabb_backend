# Buyer Order, Review, and Report APIs - Quick Summary

## ✅ What's Available Now

### 1. **View Orders** ✅
- **API**: `GET /api/user/orders/`
- **What it shows**: All orders buyer paid for with status (packed, shipped, delivered)
- **New field**: `reviewSubmitted` - shows if review was already submitted

### 2. **Order Status Tracking** ✅
Order statuses: `pending` → `packed` → `ready` → `shipped` → `delivered`
- Buyers can see current status of each order
- Tracking number available when shipped

### 3. **Submit Reviews** ✅ NEW
- **API**: `POST /api/user/reviews/create/`
- **Requirements**: 
  - Order must be `delivered`
  - Rating: 1-5 stars
  - Comment: Optional text (max 1000 chars)
- **Limit**: One review per order

### 4. **View Product Reviews** ✅ NEW
- **API**: `GET /api/user/reviews/product/<product_id>/`
- Shows all reviews for a product with buyer info, rating, and comments

### 5. **Get Seller Rating** ✅ NEW
- **API**: `GET /api/user/reviews/seller/<seller_id>/rating/`
- Shows average rating, total reviews, and rating distribution

### 6. **Report Seller to Admin** ✅ NEW
- **API**: `POST /api/user/disputes/create/`
- **Dispute Types**: 
  - `product_quality`
  - `delivery_issue`
  - `payment_dispute`
- **Description**: Message visible to admin
- **Result**: Creates a case that admin can review and manage

## 📋 Complete Buyer Flow

1. **Buyer pays** → Order created with `status: "pending"`, `paymentStatus: "pending"`
2. **Payment completed** → `status: "packed"`, `paymentStatus: "completed"`
3. **Seller ships** → `status: "shipped"` (with tracking number)
4. **Item delivered** → `status: "delivered"` ✅
5. **Buyer can now**:
   - ✅ Submit review (rating + comment)
   - ✅ Report seller to admin (if issue)

## 🔑 Key Features

- ✅ Buyers see all paid orders
- ✅ Real-time order status tracking
- ✅ Review system with 1-5 star ratings
- ✅ Review comments
- ✅ Report system with description for admin
- ✅ One review per order (prevents duplicates)
- ✅ Reviews only for delivered orders

## 📚 Documentation

Full API documentation: See `BUYER_ORDER_REVIEW_API_DOCUMENTATION.md`

## 🎯 Quick Test

```bash
# 1. Get orders
GET /api/user/orders/
Authorization: Bearer <token>

# 2. Submit review (after delivery)
POST /api/user/reviews/create/
{
  "orderId": "order_id",
  "rating": 5,
  "comment": "Great product!"
}

# 3. Report seller
POST /api/user/disputes/create/
{
  "orderId": "order_id",
  "disputeType": "product_quality",
  "description": "Product is damaged"
}
```

---

**All APIs are ready to use!** 🚀

