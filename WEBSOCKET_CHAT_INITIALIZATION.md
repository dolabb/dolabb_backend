# 💬 WebSocket Chat Initialization Guide

## 📋 Overview

This guide explains how to:

1. **Get or create a `conversationId`** for WebSocket chat
2. **Initialize the first chat** between two users
3. **Connect to WebSocket** and send messages

---

## 🔑 Getting Conversation ID

There are **two ways** to get a `conversationId`:

### Method 1: Get Existing Conversations (Recommended)

If a conversation already exists between two users, retrieve it from the list:

**Endpoint:** `GET /api/chat/conversations/`

**Request:**

```bash
GET https://dolabb-backend.onrender.com/api/chat/conversations/
Headers:
  Authorization: Bearer {your_jwt_token}
```

**Response:**

```json
{
  "success": true,
  "conversations": [
    {
      "id": "691c7f09e8c4f33957183a48",
      "conversationId": "691c7f09e8c4f33957183a48",
      "otherUser": {
        "id": "507f1f77bcf86cd799439012",
        "username": "john_doe",
        "profileImage": "https://..."
      },
      "lastMessage": "Hello!",
      "lastMessageAt": "2025-11-18T14:13:31.578000",
      "unreadCount": "1",
      "productId": null
    }
  ]
}
```

**Extract `conversationId`:**

```javascript
const conversations = response.data.conversations;
const conversationId = conversations[0].conversationId; // "691c7f09e8c4f33957183a48"
```

---

### Method 2: Create Conversation by Sending First Message

If no conversation exists, **send the first message via REST API**. This will
automatically create a conversation and return the `conversationId`.

**Endpoint:** `POST /api/chat/send/`

**Request:**

```bash
POST https://dolabb-backend.onrender.com/api/chat/send/
Headers:
  Authorization: Bearer {your_jwt_token}
  Content-Type: application/json

Body:
{
  "receiverId": "507f1f77bcf86cd799439012",
  "text": "Hello! This is the first message.",
  "productId": null,  // Optional: if chatting about a product
  "attachments": [],  // Optional: array of file URLs
  "offerId": null     // Optional: if sending an offer
}
```

**Response:**

```json
{
  "success": true,
  "message": {
    "id": "691c7f0be8c4f33957183a49",
    "text": "Hello! This is the first message.",
    "timestamp": "2025-11-18T14:13:30.161000"
  }
}
```

**Get `conversationId` from the message:** After sending the message, you need
to fetch the conversation. The conversation is automatically created when you
send the first message. You can then:

1. **Get conversations list** (Method 1) to find the new conversation
2. **Or query the message** to get its `conversation_id` field

**Note:** The REST API response doesn't directly return `conversationId`, so
after sending the first message, call `GET /api/chat/conversations/` to get the
newly created conversation.

---

## 🚀 First Chat Initialization Flow

### Complete Flow for First Chat:

#### Step 1: Check if Conversation Exists

```javascript
// Get all conversations
const response = await fetch(
  'https://dolabb-backend.onrender.com/api/chat/conversations/',
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);

const data = await response.json();
const existingConversation = data.conversations.find(
  conv => conv.otherUser.id === receiverId
);
```

#### Step 2: Create Conversation if Needed

If no conversation exists, send the first message via REST API:

```javascript
if (!existingConversation) {
  // Send first message to create conversation
  const firstMessageResponse = await fetch(
    'https://dolabb-backend.onrender.com/api/chat/send/',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        receiverId: receiverId,
        text: 'Hello!', // First message text
        productId: null,
        attachments: [],
        offerId: null,
      }),
    }
  );

  // After sending, get the conversation list again to get conversationId
  const conversationsResponse = await fetch(
    'https://dolabb-backend.onrender.com/api/chat/conversations/',
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const conversationsData = await conversationsResponse.json();
  const newConversation = conversationsData.conversations.find(
    conv => conv.otherUser.id === receiverId
  );

  conversationId = newConversation.conversationId;
} else {
  conversationId = existingConversation.conversationId;
}
```

#### Step 3: Connect to WebSocket

Once you have the `conversationId`, connect to the WebSocket **with
authentication token**:

```javascript
const ws = new WebSocket(
  `wss://dolabb-backend.onrender.com/ws/chat/${conversationId}/?token=${your_jwt_token}`
);

ws.onopen = () => {
  console.log('✅ Connected to chat WebSocket!');
};

ws.onmessage = event => {
  const data = JSON.parse(event.data);
  console.log('Received message:', data);

  if (data.type === 'chat_message') {
    // Handle incoming message
    handleIncomingMessage(data.message);
  }
};

ws.onerror = error => {
  console.error('WebSocket Error:', error);
};

ws.onclose = () => {
  console.log('WebSocket Disconnected');
};
```

#### Step 4: Send Messages via WebSocket

```javascript
function sendChatMessage(text, receiverId) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: 'chat_message',
        senderId: currentUserId,
        receiverId: receiverId,
        text: text,
        attachments: [],
        offerId: null,
        productId: null,
      })
    );
  }
}
```

---

## 📝 Complete Example: React/JavaScript Implementation

```javascript
class ChatService {
  constructor(token, currentUserId) {
    this.token = token;
    this.currentUserId = currentUserId;
    this.ws = null;
    this.conversationId = null;
  }

  // Step 1: Initialize or get conversation
  async initializeConversation(receiverId, firstMessage = null) {
    try {
      // Check if conversation exists
      const conversationsResponse = await fetch(
        'https://dolabb-backend.onrender.com/api/chat/conversations/',
        {
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        }
      );

      const conversationsData = await conversationsResponse.json();
      let conversation = conversationsData.conversations.find(
        conv => conv.otherUser.id === receiverId
      );

      // If no conversation exists, create one by sending first message
      if (!conversation) {
        if (!firstMessage) {
          throw new Error(
            'First message is required to create a new conversation'
          );
        }

        // Send first message via REST API
        await fetch('https://dolabb-backend.onrender.com/api/chat/send/', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${this.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            receiverId: receiverId,
            text: firstMessage,
            productId: null,
            attachments: [],
            offerId: null,
          }),
        });

        // Get the newly created conversation
        const newConversationsResponse = await fetch(
          'https://dolabb-backend.onrender.com/api/chat/conversations/',
          {
            headers: {
              Authorization: `Bearer ${this.token}`,
            },
          }
        );

        const newConversationsData = await newConversationsResponse.json();
        conversation = newConversationsData.conversations.find(
          conv => conv.otherUser.id === receiverId
        );
      }

      this.conversationId = conversation.conversationId;
      return this.conversationId;
    } catch (error) {
      console.error('Error initializing conversation:', error);
      throw error;
    }
  }

  // Step 2: Connect to WebSocket
  connectWebSocket(onMessage, onError, onClose) {
    if (!this.conversationId) {
      throw new Error(
        'Conversation ID is required. Call initializeConversation() first.'
      );
    }

    this.ws = new WebSocket(
      `wss://dolabb-backend.onrender.com/ws/chat/${this.conversationId}/?token=${this.token}`
    );

    this.ws.onopen = () => {
      console.log('✅ WebSocket Connected');
    };

    this.ws.onmessage = event => {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    };

    this.ws.onerror = error => {
      console.error('WebSocket Error:', error);
      if (onError) onError(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket Disconnected');
      if (onClose) onClose();
    };
  }

  // Step 3: Send message via WebSocket
  sendMessage(
    text,
    receiverId,
    attachments = [],
    offerId = null,
    productId = null
  ) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    this.ws.send(
      JSON.stringify({
        type: 'chat_message',
        senderId: this.currentUserId,
        receiverId: receiverId,
        text: text,
        attachments: attachments,
        offerId: offerId,
        productId: productId,
      })
    );
  }

  // Disconnect WebSocket
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage Example:
const chatService = new ChatService(token, currentUserId);

// Initialize conversation (creates if doesn't exist)
await chatService.initializeConversation(
  receiverId,
  'Hello! This is my first message.'
);

// Connect to WebSocket
chatService.connectWebSocket(
  data => {
    // Handle incoming messages
    if (data.type === 'chat_message') {
      console.log('New message:', data.message);
    }
  },
  error => {
    // Handle errors
    console.error('WebSocket error:', error);
  },
  () => {
    // Handle disconnect
    console.log('Disconnected');
  }
);

// Send messages
chatService.sendMessage('Hello from WebSocket!', receiverId);
```

---

## 🔄 Alternative: Initialize via WebSocket Directly

**Note:** You can also initialize a conversation directly via WebSocket, but you
still need a `conversationId`. The system will create the conversation
automatically when the first message is sent.

However, **this approach is not recommended** because:

1. You need to know or generate a conversation ID beforehand
2. The conversation might not exist yet
3. It's better to use REST API first to ensure the conversation exists

---

## 📊 Message Format

### Sending Message via WebSocket:

```json
{
  "type": "chat_message",
  "senderId": "507f1f77bcf86cd799439011",
  "receiverId": "507f1f77bcf86cd799439012",
  "text": "Hello, this is a test message",
  "attachments": [],
  "offerId": null,
  "productId": null
}
```

### Receiving Message via WebSocket:

```json
{
  "type": "chat_message",
  "message": {
    "id": "691c7f0be8c4f33957183a49",
    "text": "Hello, this is a test message",
    "sender": "me",
    "timestamp": "2025-11-18T14:13:30.161000",
    "attachments": []
  }
}
```

---

## 💰 Offer Management via WebSocket

You can send offers, counter offers, accept, and reject offers directly through
WebSocket for real-time negotiation.

### ⚠️ Important: Authentication Required

**All WebSocket connections now require authentication.** You must include your
JWT token in the WebSocket URL:

```javascript
const ws = new WebSocket(
  `wss://dolabb-backend.onrender.com/ws/chat/${conversationId}/?token=${your_jwt_token}`
);
```

Without a valid token, the connection will be rejected with code `4001`
(Unauthorized).

---

### 1. Send Offer

**Message Type:** `send_offer`

**Who can send:** Buyer

**Request:**

```json
{
  "type": "send_offer",
  "productId": "507f1f77bcf86cd799439011",
  "offerAmount": 150.0,
  "receiverId": "507f1f77bcf86cd799439012",
  "text": "I'd like to offer $150 for this product", // Optional
  "shippingAddress": "123 Main St", // Optional
  "zipCode": "12345", // Optional
  "houseNumber": "Apt 4B" // Optional
}
```

**Response (broadcasted to all connected users in conversation):**

```json
{
  "type": "offer_sent",
  "offer": {
    "id": "691c7f0be8c4f33957183a49",
    "productId": "507f1f77bcf86cd799439011",
    "buyerId": "507f1f77bcf86cd799439010",
    "sellerId": "507f1f77bcf86cd799439012",
    "offerAmount": 150.0,
    "originalPrice": 200.0,
    "status": "pending",
    "createdAt": "2025-11-18T14:13:30.161000"
  },
  "message": {
    "id": "691c7f0be8c4f33957183a50",
    "text": "Made an offer of $150",
    "timestamp": "2025-11-18T14:13:30.161000"
  }
}
```

**JavaScript Example:**

```javascript
function sendOffer(productId, offerAmount, receiverId, shippingDetails = {}) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: 'send_offer',
        productId: productId,
        offerAmount: offerAmount,
        receiverId: receiverId,
        text: `I'd like to offer $${offerAmount} for this product`,
        shippingAddress: shippingDetails.address,
        zipCode: shippingDetails.zipCode,
        houseNumber: shippingDetails.houseNumber,
      })
    );
  }
}
```

---

### 2. Counter Offer

**Message Type:** `counter_offer`

**Who can send:** Seller (in response to buyer's offer)

**Request:**

```json
{
  "type": "counter_offer",
  "offerId": "691c7f0be8c4f33957183a49",
  "counterAmount": 175.0,
  "receiverId": "507f1f77bcf86cd799439010",
  "text": "I can do $175" // Optional
}
```

**Response (broadcasted to all connected users in conversation):**

```json
{
  "type": "offer_countered",
  "offer": {
    "id": "691c7f0be8c4f33957183a49",
    "counterAmount": 175.0,
    "status": "countered",
    "updatedAt": "2025-11-18T14:15:30.161000"
  },
  "message": {
    "id": "691c7f0be8c4f33957183a51",
    "text": "Countered with $175",
    "timestamp": "2025-11-18T14:15:30.161000"
  }
}
```

**JavaScript Example:**

```javascript
function counterOffer(offerId, counterAmount, receiverId) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: 'counter_offer',
        offerId: offerId,
        counterAmount: counterAmount,
        receiverId: receiverId,
        text: `I can do $${counterAmount}`,
      })
    );
  }
}
```

---

### 3. Accept Offer

**Message Type:** `accept_offer`

**Who can send:**

- **Seller** can accept buyer's original offer (when status is `pending`)
- **Buyer** can accept seller's counter offer (when status is `countered`)

**Request:**

```json
{
  "type": "accept_offer",
  "offerId": "691c7f0be8c4f33957183a49",
  "receiverId": "507f1f77bcf86cd799439010",
  "text": "Deal! Let's proceed with the purchase" // Optional
}
```

**Response (broadcasted to all connected users in conversation):**

```json
{
  "type": "offer_accepted",
  "offer": {
    "id": "691c7f0be8c4f33957183a49",
    "status": "accepted",
    "updatedAt": "2025-11-18T14:20:30.161000"
  },
  "message": {
    "id": "691c7f0be8c4f33957183a52",
    "text": "Offer accepted",
    "timestamp": "2025-11-18T14:20:30.161000"
  }
}
```

**JavaScript Example:**

```javascript
function acceptOffer(offerId, receiverId) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: 'accept_offer',
        offerId: offerId,
        receiverId: receiverId,
        text: "Deal! Let's proceed",
      })
    );
  }
}
```

---

### 4. Reject Offer

**Message Type:** `reject_offer`

**Who can send:** Seller (rejecting buyer's offer)

**Request:**

```json
{
  "type": "reject_offer",
  "offerId": "691c7f0be8c4f33957183a49",
  "receiverId": "507f1f77bcf86cd799439010",
  "text": "Sorry, I can't accept this offer" // Optional
}
```

**Response (broadcasted to all connected users in conversation):**

```json
{
  "type": "offer_rejected",
  "offer": {
    "id": "691c7f0be8c4f33957183a49",
    "status": "rejected",
    "updatedAt": "2025-11-18T14:25:30.161000"
  },
  "message": {
    "id": "691c7f0be8c4f33957183a53",
    "text": "Offer rejected",
    "timestamp": "2025-11-18T14:25:30.161000"
  }
}
```

**JavaScript Example:**

```javascript
function rejectOffer(offerId, receiverId) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: 'reject_offer',
        offerId: offerId,
        receiverId: receiverId,
        text: "Sorry, I can't accept this offer",
      })
    );
  }
}
```

---

### 📋 Complete Offer Flow Example

```javascript
// Initialize WebSocket with authentication
const ws = new WebSocket(
  `wss://dolabb-backend.onrender.com/ws/chat/${conversationId}/?token=${token}`
);

ws.onmessage = event => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case 'offer_sent':
      console.log('New offer:', data.offer);
      // Update UI to show offer
      break;

    case 'offer_countered':
      console.log('Counter offer:', data.offer);
      // Update UI to show counter offer
      // Buyer can now accept or make new offer
      break;

    case 'offer_accepted':
      console.log('Offer accepted!', data.offer);
      // Update UI, proceed to checkout
      break;

    case 'offer_rejected':
      console.log('Offer rejected', data.offer);
      // Update UI
      break;

    case 'error':
      console.error('Error:', data.message);
      break;
  }
};

// Buyer sends offer
sendOffer('product123', 150.0, 'seller456', {
  address: '123 Main St',
  zipCode: '12345',
  houseNumber: 'Apt 4B',
});

// Seller counters
counterOffer('offer789', 175.0, 'buyer123');

// Buyer accepts counter
acceptOffer('offer789', 'seller456');
```

---

### ⚠️ Error Handling

All offer operations return error messages if something goes wrong:

```json
{
  "type": "error",
  "message": "Offer not found"
}
```

**Common Errors:**

- `"Authentication required"` - Token missing or invalid
- `"productId, offerAmount, and receiverId are required"` - Missing required
  fields
- `"Offer not found"` - Invalid offer ID
- `"Only seller can accept a pending offer"` - Wrong user trying to accept
- `"Only buyer can accept a counter offer"` - Wrong user trying to accept
  counter
- `"Cannot accept offer with status: rejected"` - Offer already rejected

---

## ✅ Summary

### Quick Start Checklist:

1. ✅ **Get JWT Token** (from login/register)
2. ✅ **Check for existing conversation** via `GET /api/chat/conversations/`
3. ✅ **If no conversation exists**, send first message via
   `POST /api/chat/send/`
4. ✅ **Get `conversationId`** from conversations list
5. ✅ **Connect to WebSocket** using
   `wss://dolabb-backend.onrender.com/ws/chat/{conversationId}/`
6. ✅ **Send/receive messages** via WebSocket

### Key Points:

- **Conversation is automatically created** when you send the first message
- **You must have a `conversationId`** before connecting to WebSocket
- **First message can be sent via REST API** to create the conversation
- **Subsequent messages** can be sent via WebSocket for real-time communication
- **Both users** need to connect to the same `conversationId` to chat

---

## 🐛 Troubleshooting

### Issue: "Conversation not found" when connecting to WebSocket

**Solution:** Make sure you've created the conversation first by sending a
message via REST API (`POST /api/chat/send/`).

### Issue: "WebSocket connection failed"

**Solution:**

1. Verify the `conversationId` is correct
2. Check if the conversation exists via `GET /api/chat/conversations/`
3. Ensure you're using `wss://` (not `ws://`) for HTTPS
4. Verify your JWT token is valid

### Issue: "First message not creating conversation"

**Solution:**

1. Check that both `senderId` and `receiverId` are valid user IDs
2. Verify your authentication token is valid
3. Check server logs for errors

---

**Need Help?** Check the main WebSocket documentation: `WEBSOCKET_SETUP.md` and
`WEBSOCKET_TESTING_GUIDE.md`
