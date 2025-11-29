# Messages API Response Format Documentation

This document describes the REST API response format for the paginated messages endpoint after implementing the pagination requirements.

## Table of Contents

1. [API Endpoint](#api-endpoint)
2. [Request Parameters](#request-parameters)
3. [Response Structure](#response-structure)
4. [Message Object Structure](#message-object-structure)
5. [Pagination Behavior](#pagination-behavior)
6. [Example Responses](#example-responses)
7. [Edge Cases](#edge-cases)
8. [Testing Scenarios](#testing-scenarios)

---

## API Endpoint

**Endpoint:** `GET /api/chat/conversations/{conversationId}/messages/`

**Method:** `GET`

**Authentication:** Required (JWT token in header)

**URL Parameters:**
- `conversationId` (string, required) - The conversation ID

---

## Request Parameters

**Query Parameters:**

| Parameter | Type   | Required | Default | Description                          |
| --------- | ------ | -------- | ------- | ------------------------------------ |
| `page`    | number | No       | 1       | Page number (1-indexed)              |
| `limit`   | number | No       | 50      | Number of messages per page          |

**Example Request:**

```
GET /api/chat/conversations/507f1f77bcf86cd799439012/messages/?page=1&limit=4
```

---

## Response Structure

### Success Response

**Status Code:** `200 OK`

```json
{
  "success": true,
  "messages": [
    // Array of message objects (see Message Object Structure below)
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 4,
    "totalItems": 15
  }
}
```

### Error Response

**Status Code:** `404 Not Found` or `500 Internal Server Error`

```json
{
  "success": false,
  "error": "Error message description"
}
```

---

## Message Object Structure

Each message in the `messages` array follows this structure:

### Text Message

```json
{
  "id": "67890abcdef1234567890123",
  "text": "Hello, how are you?",
  "senderId": "507f1f77bcf86cd799439011",
  "receiverId": "507f191e810c19729de860ea",
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
}
```

### Offer Message

```json
{
  "id": "67890abcdef1234567890124",
  "text": "Made an offer of $1300",
  "senderId": "507f1f77bcf86cd799439011",
  "receiverId": "507f191e810c19729de860ea",
  "isSender": true,
  "sender": "me",
  "senderName": "John Doe",
  "timestamp": "2025-01-15T10:35:20.789012",
  "createdAt": "2025-01-15T10:35:20.789012",
  "attachments": [],
  "offerId": "507f1f77bcf86cd799439013",
  "productId": "507f1f77bcf86cd799439014",
  "messageType": "offer",
  "isRead": false,
  "offer": {
    "id": "507f1f77bcf86cd799439013",
    "offerAmount": 1300.0,
    "counterAmount": null,
    "originalPrice": 1499.0,
    "status": "pending",
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
  }
}
```

### Message Fields

| Field         | Type    | Description                                    |
| ------------- | ------- | ---------------------------------------------- |
| `id`          | string  | Unique message ID                              |
| `text`        | string  | Message text content                           |
| `senderId`    | string  | ID of the user who sent the message           |
| `receiverId`  | string  | ID of the user who receives the message       |
| `isSender`    | boolean | `true` if current user sent this message      |
| `sender`      | string  | `"me"` if current user sent, `"other"` if not |
| `senderName`  | string  | Full name of the sender                        |
| `timestamp`   | string  | ISO 8601 timestamp of message creation        |
| `createdAt`   | string  | ISO 8601 timestamp (same as timestamp)        |
| `attachments` | array   | Array of attachment URLs                       |
| `offerId`     | string  | Offer ID if message is offer-related, else null |
| `productId`   | string  | Product ID if message is product-related, else null |
| `messageType` | string  | `"text"` or `"offer"`                         |
| `isRead`      | boolean | Whether the message has been read              |
| `offer`       | object  | Complete offer object (only if `messageType` is `"offer"`) |

---

## Pagination Behavior

### Message Ordering

- **Messages are ordered by `createdAt` in descending order (newest first)**
- **Page 1 contains the most recent messages**
- **Higher page numbers contain older messages**

### Pagination Metadata

The `pagination` object contains:

| Field        | Type   | Description                          |
| ------------ | ------ | ------------------------------------ |
| `currentPage` | number | The current page number (1-indexed)  |
| `totalPages` | number | Total number of pages available      |
| `totalItems` | number | Total number of messages in conversation |

### Pagination Logic

- **Page 1** = Most recent messages (newest)
- **Page 2** = Next most recent messages (older)
- **Page N** = Older messages

**Example with 15 messages, limit = 4:**

- **Page 1:** Messages 15, 14, 13, 12 (newest 4)
- **Page 2:** Messages 11, 10, 9, 8
- **Page 3:** Messages 7, 6, 5, 4
- **Page 4:** Messages 3, 2, 1 (oldest 3)

---

## Example Responses

### Example 1: Page 1 with 4 Messages (Limit = 4)

**Request:**
```
GET /api/chat/conversations/507f1f77bcf86cd799439012/messages/?page=1&limit=4
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": "msg_15",
      "text": "Latest message",
      "senderId": "user_1",
      "receiverId": "user_2",
      "isSender": true,
      "sender": "me",
      "senderName": "John Doe",
      "timestamp": "2025-01-15T15:00:00.000000",
      "createdAt": "2025-01-15T15:00:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    },
    {
      "id": "msg_14",
      "text": "Second latest",
      "senderId": "user_2",
      "receiverId": "user_1",
      "isSender": false,
      "sender": "other",
      "senderName": "Jane Smith",
      "timestamp": "2025-01-15T14:55:00.000000",
      "createdAt": "2025-01-15T14:55:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    },
    {
      "id": "msg_13",
      "text": "Third latest",
      "senderId": "user_1",
      "receiverId": "user_2",
      "isSender": true,
      "sender": "me",
      "senderName": "John Doe",
      "timestamp": "2025-01-15T14:50:00.000000",
      "createdAt": "2025-01-15T14:50:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    },
    {
      "id": "msg_12",
      "text": "Fourth latest",
      "senderId": "user_2",
      "receiverId": "user_1",
      "isSender": false,
      "sender": "other",
      "senderName": "Jane Smith",
      "timestamp": "2025-01-15T14:45:00.000000",
      "createdAt": "2025-01-15T14:45:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 4,
    "totalItems": 15
  }
}
```

### Example 2: Page 2 (Older Messages)

**Request:**
```
GET /api/chat/conversations/507f1f77bcf86cd799439012/messages/?page=2&limit=4
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": "msg_11",
      "text": "Fifth message",
      "senderId": "user_1",
      "receiverId": "user_2",
      "isSender": true,
      "sender": "me",
      "senderName": "John Doe",
      "timestamp": "2025-01-15T14:40:00.000000",
      "createdAt": "2025-01-15T14:40:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    },
    {
      "id": "msg_10",
      "text": "Sixth message",
      "senderId": "user_2",
      "receiverId": "user_1",
      "isSender": false,
      "sender": "other",
      "senderName": "Jane Smith",
      "timestamp": "2025-01-15T14:35:00.000000",
      "createdAt": "2025-01-15T14:35:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    },
    {
      "id": "msg_9",
      "text": "Seventh message",
      "senderId": "user_1",
      "receiverId": "user_2",
      "isSender": true,
      "sender": "me",
      "senderName": "John Doe",
      "timestamp": "2025-01-15T14:30:00.000000",
      "createdAt": "2025-01-15T14:30:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    },
    {
      "id": "msg_8",
      "text": "Eighth message",
      "senderId": "user_2",
      "receiverId": "user_1",
      "isSender": false,
      "sender": "other",
      "senderName": "Jane Smith",
      "timestamp": "2025-01-15T14:25:00.000000",
      "createdAt": "2025-01-15T14:25:00.000000",
      "attachments": [],
      "offerId": null,
      "productId": null,
      "messageType": "text",
      "isRead": false
    }
  ],
  "pagination": {
    "currentPage": 2,
    "totalPages": 4,
    "totalItems": 15
  }
}
```

### Example 3: Empty Conversation

**Request:**
```
GET /api/chat/conversations/507f1f77bcf86cd799439012/messages/?page=1&limit=4
```

**Response:**
```json
{
  "success": true,
  "messages": [],
  "pagination": {
    "currentPage": 1,
    "totalPages": 0,
    "totalItems": 0
  }
}
```

### Example 4: Page Beyond Available Pages

**Request:**
```
GET /api/chat/conversations/507f1f77bcf86cd799439012/messages/?page=10&limit=4
```

**Response:**
```json
{
  "success": true,
  "messages": [],
  "pagination": {
    "currentPage": 10,
    "totalPages": 4,
    "totalItems": 15
  }
}
```

### Example 5: Message with Offer

**Request:**
```
GET /api/chat/conversations/507f1f77bcf86cd799439012/messages/?page=1&limit=4
```

**Response (showing one offer message):**
```json
{
  "success": true,
  "messages": [
    {
      "id": "msg_15",
      "text": "Made an offer of $1300",
      "senderId": "user_1",
      "receiverId": "user_2",
      "isSender": true,
      "sender": "me",
      "senderName": "John Doe",
      "timestamp": "2025-01-15T15:00:00.000000",
      "createdAt": "2025-01-15T15:00:00.000000",
      "attachments": [],
      "offerId": "offer_123",
      "productId": "product_456",
      "messageType": "offer",
      "isRead": false,
      "offer": {
        "id": "offer_123",
        "offerAmount": 1300.0,
        "counterAmount": null,
        "originalPrice": 1499.0,
        "status": "pending",
        "shippingCost": 25.0,
        "expirationDate": "2025-01-22T15:00:00.000000",
        "product": {
          "id": "product_456",
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
      }
    }
    // ... other messages
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 4,
    "totalItems": 15
  }
}
```

---

## Edge Cases

### 1. Empty Conversation

- Returns empty `messages` array
- `totalPages` = 0
- `totalItems` = 0
- `currentPage` = requested page (usually 1)

### 2. Requesting Page Beyond Available Pages

- Returns empty `messages` array
- `currentPage` = requested page number
- `totalPages` = actual total pages
- `totalItems` = actual total items

### 3. Less Than One Page of Messages

- Returns all messages in `messages` array
- `totalPages` = 1
- `totalItems` = number of messages

### 4. Invalid Page Number (Negative or Zero)

- Page is automatically set to 1
- Returns page 1 results

### 5. Conversation Not Found

**Response:**
```json
{
  "success": false,
  "error": "Conversation not found"
}
```

**Status Code:** `404 Not Found`

### 6. Unauthorized Access

**Response:**
```json
{
  "success": false,
  "error": "Not authorized to view this conversation"
}
```

**Status Code:** `404 Not Found`

---

## Testing Scenarios

### Scenario 1: Conversation with 15 Messages, Limit = 4

**Test Cases:**

1. **Page 1** - Should return messages 15, 14, 13, 12 (newest 4)
2. **Page 2** - Should return messages 11, 10, 9, 8
3. **Page 3** - Should return messages 7, 6, 5, 4
4. **Page 4** - Should return messages 3, 2, 1 (oldest 3)
5. **Page 5** - Should return empty array with `currentPage: 5`, `totalPages: 4`

**Expected Pagination:**
- `totalPages`: 4
- `totalItems`: 15

### Scenario 2: Empty Conversation

**Test Cases:**

1. **Page 1** - Should return empty array
2. **Any Page** - Should return empty array

**Expected Pagination:**
- `totalPages`: 0
- `totalItems`: 0

### Scenario 3: Conversation with 3 Messages, Limit = 4

**Test Cases:**

1. **Page 1** - Should return all 3 messages
2. **Page 2** - Should return empty array

**Expected Pagination:**
- `totalPages`: 1
- `totalItems`: 3

### Scenario 4: Conversation with Exactly 4 Messages, Limit = 4

**Test Cases:**

1. **Page 1** - Should return all 4 messages
2. **Page 2** - Should return empty array

**Expected Pagination:**
- `totalPages`: 1
- `totalItems`: 4

---

## Implementation Details

### Changes Made

1. ✅ **Message Ordering:** Changed from ascending to descending order
   - Before: `.order_by('created_at')` (oldest first)
   - After: `.order_by('-created_at')` (newest first)

2. ✅ **Message Structure:** Added `createdAt` and `isRead` fields
   - `createdAt`: ISO 8601 timestamp (same as `timestamp`)
   - `isRead`: Boolean indicating read status

3. ✅ **Edge Case Handling:**
   - Empty conversations return correct pagination metadata
   - Invalid page numbers default to page 1
   - Pages beyond available pages return empty array with correct metadata

4. ✅ **Complete Offer Objects:**
   - Offer messages include full offer object with product details
   - All offer fields included (shippingCost, expirationDate, etc.)
   - Complete product information (brand, category, etc.)

### Key Points

- **Page 1 = Newest messages** (most recent)
- **Higher page numbers = Older messages** (less recent)
- **Messages ordered by createdAt DESC** (newest first)
- **All message fields included** as per requirements
- **Complete offer objects** for offer-related messages

---

## Frontend Integration Notes

### Initial Load

```javascript
// Load page 1 with limit 4
const response = await fetch(
  `/api/chat/conversations/${conversationId}/messages/?page=1&limit=4`
);
const data = await response.json();
// data.messages contains the 4 most recent messages
```

### Load More (Scroll Up)

```javascript
// Load next page (older messages)
const nextPage = currentPage + 1;
const response = await fetch(
  `/api/chat/conversations/${conversationId}/messages/?page=${nextPage}&limit=4`
);
const data = await response.json();
// Prepend data.messages to existing messages array
```

### Check if More Pages Available

```javascript
const hasMorePages = currentPage < pagination.totalPages;
```

### Handle Empty Results

```javascript
if (data.messages.length === 0) {
  // No more messages to load
  // Check if page exceeds totalPages
  if (data.pagination.currentPage > data.pagination.totalPages) {
    // User requested page beyond available pages
  }
}
```

---

## Summary

The Messages API now:

1. ✅ Returns messages in **descending order by createdAt** (newest first)
2. ✅ Supports `page` and `limit` query parameters
3. ✅ Returns pagination metadata with `currentPage`, `totalPages`, and `totalItems`
4. ✅ Handles edge cases (empty conversations, invalid page numbers)
5. ✅ Includes all required message fields (`createdAt`, `isRead`, etc.)
6. ✅ Includes complete offer objects with all fields for offer messages
7. ✅ Uses ISO 8601 format for timestamps

**Last Updated:** January 15, 2025  
**Version:** 2.0

