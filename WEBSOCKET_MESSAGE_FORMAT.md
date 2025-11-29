# WebSocket Message Format Documentation

This document describes the current WebSocket message format after the backend improvements. All messages now follow a consistent structure with complete data.

## Table of Contents

1. [Standard Message Structure](#standard-message-structure)
2. [Chat Message (`chat_message`)](#chat-message-chat_message)
3. [Offer Sent (`offer_sent`)](#offer-sent-offer_sent)
4. [Offer Countered (`offer_countered`)](#offer-countered-offer_countered)
5. [Offer Accepted (`offer_accepted`)](#offer-accepted-offer_accepted)
6. [Offer Rejected (`offer_rejected`)](#offer-rejected-offer_rejected)
7. [Error Messages](#error-messages)
8. [User Status Messages](#user-status-messages)
9. [Online Users Message](#online-users-message)

---

## Standard Message Structure

All WebSocket messages now follow this consistent structure:

```json
{
  "type": "message_type",
  "message": {
    "id": "unique_message_id",
    "text": "message text",
    "senderId": "user_id",
    "receiverId": "user_id",
    "conversationId": "conversation_id",
    "isSender": true/false,
    "sender": "me" | "other",
    "senderName": "User Full Name",
    "timestamp": "2025-01-15T10:30:45.123456",
    "createdAt": "2025-01-15T10:30:45.123456",
    "attachments": [],
    "offerId": "offer_id" | null,
    "productId": "product_id" | null,
    "messageType": "text" | "offer",
    "isRead": false
  },
  "offer": { /* Complete offer object for offer-related messages */ },
  "conversationId": "conversation_id"
}
```

---

## Chat Message (`chat_message`)

**Type:** `chat_message`

**When:** Regular text messages sent between users

**Response Format:**

```json
{
  "type": "chat_message",
  "message": {
    "id": "67890abcdef1234567890123",
    "text": "Hello, how are you?",
    "senderId": "507f1f77bcf86cd799439011",
    "receiverId": "507f191e810c19729de860ea",
    "conversationId": "507f1f77bcf86cd799439012",
    "isSender": true,
    "sender": "me",
    "senderName": "John Doe",
    "timestamp": "2025-01-15T10:30:45.123456",
    "createdAt": "2025-01-15T10:30:45.123456",
    "attachments": [],
    "offerId": null,
    "productId": null,
    "messageType": "text",
    "isRead": false
  },
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Key Changes:**
- ✅ Always includes `conversationId` at top level
- ✅ Includes both `timestamp` and `createdAt` for consistency
- ✅ Includes `isRead` status
- ✅ Complete sender/receiver information

---

## Offer Sent (`offer_sent`)

**Type:** `offer_sent`

**When:** Buyer sends an initial offer to seller

**Response Format:**

```json
{
  "type": "offer_sent",
  "message": {
    "id": "67890abcdef1234567890123",
    "text": "Made an offer of $1300",
    "senderId": "507f1f77bcf86cd799439011",
    "receiverId": "507f191e810c19729de860ea",
    "conversationId": "507f1f77bcf86cd799439012",
    "isSender": true,
    "sender": "me",
    "senderName": "John Doe",
    "timestamp": "2025-01-15T10:30:45.123456",
    "createdAt": "2025-01-15T10:30:45.123456",
    "attachments": [],
    "offerId": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "messageType": "offer",
    "isRead": false
  },
  "offer": {
    "id": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "buyerId": "507f1f77bcf86cd799439011",
    "sellerId": "507f191e810c19729de860ea",
    "offerAmount": 1300.0,
    "originalPrice": 1499.0,
    "status": "pending",
    "createdAt": "2025-01-15T10:30:45.123456",
    "updatedAt": "2025-01-15T10:30:45.123456",
    "shippingCost": 25.0,
    "expirationDate": "2025-01-22T10:30:45.123456",
    "product": {
      "id": "507f1f77bcf86cd799439014",
      "title": "Nike Air Max 270",
      "image": "https://example.com/image1.jpg",
      "images": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
      ],
      "price": 1499.0,
      "originalPrice": 1499.0,
      "currency": "SAR",
      "size": "42",
      "condition": "New",
      "brand": "Nike",
      "category": "Shoes"
    }
  },
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Key Changes:**
- ✅ Complete offer object with all fields (buyerId, sellerId, shippingCost, expirationDate)
- ✅ Full product details including brand and category
- ✅ Complete message structure with all required fields
- ✅ `messageType` is set to `"offer"`

---

## Offer Countered (`offer_countered`)

**Type:** `offer_countered`

**When:** Seller counters buyer's offer with a new amount

**Response Format:**

```json
{
  "type": "offer_countered",
  "message": {
    "id": "67890abcdef1234567890124",
    "text": "Countered with $1450",
    "senderId": "507f191e810c19729de860ea",
    "receiverId": "507f1f77bcf86cd799439011",
    "conversationId": "507f1f77bcf86cd799439012",
    "isSender": false,
    "sender": "other",
    "senderName": "Jane Smith",
    "timestamp": "2025-01-15T10:35:20.789012",
    "createdAt": "2025-01-15T10:35:20.789012",
    "attachments": [],
    "offerId": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "messageType": "offer",
    "isRead": false
  },
  "offer": {
    "id": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "buyerId": "507f1f77bcf86cd799439011",
    "sellerId": "507f191e810c19729de860ea",
    "offerAmount": 1300.0,
    "counterAmount": 1450.0,
    "originalPrice": 1499.0,
    "status": "countered",
    "createdAt": "2025-01-15T10:30:45.123456",
    "updatedAt": "2025-01-15T10:35:20.789012",
    "shippingCost": 25.0,
    "expirationDate": "2025-01-22T10:30:45.123456",
    "product": {
      "id": "507f1f77bcf86cd799439014",
      "title": "Nike Air Max 270",
      "image": "https://example.com/image1.jpg",
      "images": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
      ],
      "price": 1499.0,
      "originalPrice": 1499.0,
      "currency": "SAR",
      "size": "42",
      "condition": "New",
      "brand": "Nike",
      "category": "Shoes"
    }
  },
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Key Changes:**
- ✅ Includes `counterAmount` in offer object
- ✅ Status updated to `"countered"`
- ✅ Complete offer and product details
- ✅ Correct sender/receiver IDs (seller is sender, buyer is receiver)

---

## Offer Accepted (`offer_accepted`)

**Type:** `offer_accepted`

**When:** Seller accepts buyer's original offer OR buyer accepts seller's counter offer

**Response Format:**

```json
{
  "type": "offer_accepted",
  "message": {
    "id": "67890abcdef1234567890125",
    "text": "Offer accepted",
    "senderId": "507f191e810c19729de860ea",
    "receiverId": "507f1f77bcf86cd799439011",
    "conversationId": "507f1f77bcf86cd799439012",
    "isSender": false,
    "sender": "other",
    "senderName": "Jane Smith",
    "timestamp": "2025-01-15T10:40:10.456789",
    "createdAt": "2025-01-15T10:40:10.456789",
    "attachments": [],
    "offerId": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "messageType": "offer",
    "isRead": false
  },
  "offer": {
    "id": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "buyerId": "507f1f77bcf86cd799439011",
    "sellerId": "507f191e810c19729de860ea",
    "offerAmount": 1300.0,
    "counterAmount": null,
    "originalPrice": 1499.0,
    "status": "accepted",
    "createdAt": "2025-01-15T10:30:45.123456",
    "updatedAt": "2025-01-15T10:40:10.456789",
    "shippingCost": 25.0,
    "expirationDate": "2025-01-22T10:30:45.123456",
    "product": {
      "id": "507f1f77bcf86cd799439014",
      "title": "Nike Air Max 270",
      "image": "https://example.com/image1.jpg",
      "images": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
      ],
      "price": 1499.0,
      "originalPrice": 1499.0,
      "currency": "SAR",
      "size": "42",
      "condition": "New",
      "brand": "Nike",
      "category": "Shoes"
    }
  },
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Key Changes:**
- ✅ **NOW INCLUDES COMPLETE OFFER OBJECT** (previously only had id, status, updatedAt)
- ✅ Full product details included
- ✅ Status updated to `"accepted"`
- ✅ Complete message structure

---

## Offer Rejected (`offer_rejected`)

**Type:** `offer_rejected`

**When:** Seller rejects buyer's offer

**Response Format:**

```json
{
  "type": "offer_rejected",
  "message": {
    "id": "67890abcdef1234567890126",
    "text": "Offer rejected",
    "senderId": "507f191e810c19729de860ea",
    "receiverId": "507f1f77bcf86cd799439011",
    "conversationId": "507f1f77bcf86cd799439012",
    "isSender": false,
    "sender": "other",
    "senderName": "Jane Smith",
    "timestamp": "2025-01-15T10:42:30.123456",
    "createdAt": "2025-01-15T10:42:30.123456",
    "attachments": [],
    "offerId": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "messageType": "offer",
    "isRead": false
  },
  "offer": {
    "id": "507f1f77bcf86cd799439013",
    "productId": "507f1f77bcf86cd799439014",
    "buyerId": "507f1f77bcf86cd799439011",
    "sellerId": "507f191e810c19729de860ea",
    "offerAmount": 1300.0,
    "counterAmount": null,
    "originalPrice": 1499.0,
    "status": "rejected",
    "createdAt": "2025-01-15T10:30:45.123456",
    "updatedAt": "2025-01-15T10:42:30.123456",
    "shippingCost": 25.0,
    "expirationDate": "2025-01-22T10:30:45.123456",
    "product": {
      "id": "507f1f77bcf86cd799439014",
      "title": "Nike Air Max 270",
      "image": "https://example.com/image1.jpg",
      "images": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
      ],
      "price": 1499.0,
      "originalPrice": 1499.0,
      "currency": "SAR",
      "size": "42",
      "condition": "New",
      "brand": "Nike",
      "category": "Shoes"
    }
  },
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Key Changes:**
- ✅ **NOW INCLUDES COMPLETE OFFER OBJECT** (previously only had id, status, updatedAt)
- ✅ Full product details included
- ✅ Status updated to `"rejected"`
- ✅ Complete message structure

---

## Error Messages

**Type:** `error`

**When:** Any error occurs during WebSocket message processing

**Response Format:**

```json
{
  "type": "error",
  "message": "Error description",
  "error": "ERROR_CODE",
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Error Codes:**

| Error Code | Description |
|------------|-------------|
| `MISSING_RECEIVER_ID` | receiverId is required but not provided |
| `MISSING_REQUIRED_FIELDS` | Required fields are missing |
| `VALIDATION_ERROR` | Validation error occurred |
| `OFFER_CREATION_ERROR` | Error creating offer |
| `COUNTER_OFFER_ERROR` | Error countering offer |
| `ACCEPT_OFFER_ERROR` | Error accepting offer |
| `REJECT_OFFER_ERROR` | Error rejecting offer |
| `OFFER_NOT_FOUND` | Offer not found |
| `UNAUTHORIZED_ACTION` | User not authorized for this action |
| `INVALID_OFFER_STATUS` | Offer status is invalid for this action |
| `UNKNOWN_MESSAGE_TYPE` | Unknown message type received |
| `INVALID_JSON` | Invalid JSON format |
| `PROCESSING_ERROR` | General processing error |

**Examples:**

```json
// Missing receiver ID
{
  "type": "error",
  "message": "receiverId is required",
  "error": "MISSING_RECEIVER_ID",
  "conversationId": "507f1f77bcf86cd799439012"
}

// Offer not found
{
  "type": "error",
  "message": "Offer not found",
  "error": "OFFER_NOT_FOUND",
  "conversationId": "507f1f77bcf86cd799439012"
}

// Unauthorized action
{
  "type": "error",
  "message": "Only seller can accept a pending offer",
  "error": "UNAUTHORIZED_ACTION",
  "conversationId": "507f1f77bcf86cd799439012"
}
```

**Key Changes:**
- ✅ Always includes `error` field with error code
- ✅ Always includes `conversationId` when available
- ✅ Consistent error structure across all error types

---

## User Status Messages

**Type:** `user_status`

**When:** User goes online or offline in a conversation

**Response Format:**

```json
{
  "type": "user_status",
  "user_id": "507f1f77bcf86cd799439011",
  "status": "online",
  "onlineUsers": [
    "507f1f77bcf86cd799439011",
    "507f191e810c19729de860ea"
  ],
  "participants": [
    "507f1f77bcf86cd799439011",
    "507f191e810c19729de860ea"
  ]
}
```

**Status Values:**
- `"online"` - User came online
- `"offline"` - User went offline

---

## Online Users Message

**Type:** `online_users`

**When:** User connects to WebSocket, receives current online users

**Response Format:**

```json
{
  "type": "online_users",
  "onlineUsers": [
    "507f1f77bcf86cd799439011",
    "507f191e810c19729de860ea"
  ],
  "participants": [
    "507f1f77bcf86cd799439011",
    "507f191e810c19729de860ea"
  ]
}
```

---

## Summary of Changes

### Before vs After

#### Before:
- ❌ Missing `conversationId` in some messages
- ❌ Incomplete offer objects (only id, status, updatedAt for accepted/rejected)
- ❌ Missing fields in message structure (createdAt, isRead)
- ❌ Inconsistent error messages (no error codes, missing conversationId)
- ❌ Incomplete product details (missing brand, category)
- ❌ Missing offer fields (shippingCost, expirationDate)

#### After:
- ✅ **Always includes `conversationId`** in all messages
- ✅ **Complete offer objects** with all fields in all offer-related messages
- ✅ **Complete message structure** with all required fields
- ✅ **Structured error messages** with error codes and conversationId
- ✅ **Complete product details** including brand and category
- ✅ **All offer fields** including shippingCost and expirationDate
- ✅ **Consistent timestamps** using ISO 8601 format
- ✅ **Proper messageType** field ('text' or 'offer')

### Frontend Integration Notes

1. **Query Refetching:** Always check if query exists before refetching:
   ```javascript
   if (queryClient.getQueryState(['messages', conversationId])) {
     queryClient.invalidateQueries(['messages', conversationId]);
   }
   ```

2. **Message Type Detection:** Use `messageType` field to identify offer messages:
   ```javascript
   if (message.messageType === 'offer') {
     // Handle as offer message
   }
   ```

3. **Offer Status Updates:** Use complete offer object to update UI:
   ```javascript
   const offer = message.offer; // Complete offer object always available
   updateOfferStatus(offer.id, offer.status);
   ```

4. **Error Handling:** Use error codes for specific error handling:
   ```javascript
   if (error.error === 'OFFER_NOT_FOUND') {
     // Handle offer not found
   }
   ```

---

## Testing Checklist

- [x] All messages include `conversationId`
- [x] All offer messages include complete offer object
- [x] All messages include complete message structure
- [x] Error messages include error codes
- [x] Timestamps are in ISO format
- [x] Product details include brand and category
- [x] Offer objects include shippingCost and expirationDate
- [x] Message type is correctly set ('text' or 'offer')

---

**Last Updated:** January 15, 2025
**Version:** 2.0

