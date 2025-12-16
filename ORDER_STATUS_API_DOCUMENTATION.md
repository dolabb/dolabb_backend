# Order Status Update API - Documentation

## Allowed Order Statuses

Based on the Order model, sellers can update order status to any of these
values:

```python
['pending', 'packed', 'ready', 'shipped', 'delivered', 'cancelled']
```

### Status Descriptions:

1. **`pending`** - Order is pending (initial state)
2. **`packed`** - Order is packed and ready (automatically set after payment)
3. **`ready`** - Order is ready for shipping
4. **`shipped`** - Order has been shipped (seller action)
5. **`delivered`** - Order has been delivered (requires shipment proof)
6. **`cancelled`** - Order has been cancelled

## Current API Endpoint

### Ship Order Endpoint

**URL**: `PUT /api/products/payments/<order_id>/ship/`

**Description**: Ship order (seller action). This endpoint automatically sets
status based on shipment proof.

**Request Body**:

```json
{
  "trackingNumber": "TRACK123456",
  "shipmentProof": <file> (optional - image file),
  "shipmentProofUrl": "https://example.com/proof.jpg" (optional - URL)
}
```

**Status Logic**:

- If `shipmentProof` or `shipmentProofUrl` is provided → Status set to
  **`delivered`**
- If no shipment proof → Status set to **`shipped`**

**Response**:

```json
{
  "success": true,
  "payment": {
    "id": "order_id",
    "status": "shipped" or "delivered",
    "trackingNumber": "TRACK123456",
    "shipmentProof": "url" (if provided)
  },
  "message": "Order shipped..." or "Order marked as delivered..."
}
```

## ✅ General Order Status Update Endpoint (NEW)

**URL**: `PUT /api/products/orders/<order_id>/status/`

**Description**: Allows seller to update order status to any allowed value.

**Request Body**:

```json
{
  "status": "packed" | "ready" | "shipped" | "delivered" | "cancelled",
  "trackingNumber": "TRACK123456" (optional - recommended for shipped/delivered),
  "shipmentProof": <file> (required for "delivered" status),
  "shipmentProofUrl": "https://example.com/proof.jpg" (alternative to file upload)
}
```

**Validation**:

- ✅ Status must be one of:
  `['pending', 'packed', 'ready', 'shipped', 'delivered', 'cancelled']`
- ✅ Only seller of the order can update it
- ✅ `shipmentProof` or `shipmentProofUrl` **required** for `delivered` status
- ✅ `trackingNumber` recommended for `shipped` and `delivered` statuses

**Response**:

```json
{
  "success": true,
  "order": {
    "id": "order_id",
    "status": "shipped",
    "trackingNumber": "TRACK123456",
    "shipmentProof": "url" (if provided)
  },
  "message": "Order status updated to shipped"
}
```

**Example Requests**:

1. **Update to "ready"**:

```json
PUT /api/products/orders/694098f52d1b5c8d31b69968/status/
{
  "status": "ready"
}
```

2. **Update to "shipped"**:

```json
PUT /api/products/orders/694098f52d1b5c8d31b69968/status/
{
  "status": "shipped",
  "trackingNumber": "TRACK123456"
}
```

3. **Update to "delivered"** (requires shipment proof):

```json
PUT /api/products/orders/694098f52d1b5c8d31b69968/status/
{
  "status": "delivered",
  "trackingNumber": "TRACK123456",
  "shipmentProof": <file> OR "shipmentProofUrl": "https://example.com/proof.jpg"
}
```

4. **Update to "cancelled"**:

```json
PUT /api/products/orders/694098f52d1b5c8d31b69968/status/
{
  "status": "cancelled"
}
```

## Current Workflow

1. **Payment completed** → Order status automatically set to `packed`
2. **Seller ships** → Call `/api/products/payments/<order_id>/ship/` → Status
   becomes `shipped` or `delivered`
3. **Other statuses** → Currently no endpoint to set `ready` or manually set
   other statuses

## Summary

✅ **Allowed statuses**: `pending`, `packed`, `ready`, `shipped`, `delivered`,
`cancelled`  
✅ **General endpoint**: `PUT /api/products/orders/<order_id>/status/` - Allows
any status  
✅ **Ship endpoint**: `PUT /api/products/payments/<order_id>/ship/` - Auto-sets
shipped/delivered  
✅ **Validation**: Status must be in allowed list, shipment proof required for
delivered  
✅ **Notifications**: Automatically sent based on status change

## Status Flow Recommendations

1. **`pending`** → Initial state (set automatically)
2. **`packed`** → Set automatically after payment completion
3. **`ready`** → Seller can set when order is ready to ship
4. **`shipped`** → Seller sets when order is shipped (tracking number
   recommended)
5. **`delivered`** → Seller sets when order is delivered (shipment proof
   required)
6. **`cancelled`** → Can be set by seller or buyer (triggers cancellation
   notifications)
