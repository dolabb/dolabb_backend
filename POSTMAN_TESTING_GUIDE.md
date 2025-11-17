# Postman Testing Guide

## 📥 Importing the Collection

1. Open Postman
2. Click **Import** button (top left)
3. Select the file: `Dolabb_Backend_API.postman_collection.json`
4. The collection will be imported with all endpoints organized

## 🔧 Setting Up Variables

The collection uses variables for easy testing. Set them up:

1. Click on the collection name: **Dolabb Backend API**
2. Go to **Variables** tab
3. Set the following variables:

```
base_url: http://localhost:8000
user_token: (will be set after login)
admin_token: (will be set after admin login)
affiliate_token: (will be set after affiliate login)
product_id: (set after creating a product)
offer_id: (set after creating an offer)
conversation_id: (set after getting conversations)
order_id: (set after checkout)
notification_id: (set after creating notification)
```

## 🚀 Testing Flow

### Step 1: Authentication

1. **Admin Signup** → `POST /api/auth/admin/signup/`
   - Creates admin account
   - Returns OTP (check email)

2. **Admin Login** → `POST /api/auth/admin/login/`
   - Copy the `token` from response
   - Paste it in collection variable: `admin_token`

3. **User Signup** → `POST /api/auth/signup/`
   - Creates user account
   - Returns OTP and token
   - Copy token to `user_token` variable

4. **User Login** → `POST /api/auth/login/`
   - Get token and update `user_token` variable

### Step 2: Products

1. **Create Product** → `POST /api/products/create/`
   - Use `user_token` in Authorization header
   - Copy `product.id` from response
   - Set it in `product_id` variable

2. **Get Products** → `GET /api/products/`
   - Test filters: category, price range, search

3. **Get Product Detail** → `GET /api/products/{product_id}/`
   - Uses `product_id` variable

### Step 3: Offers

1. **Create Offer** → `POST /api/offers/create/`
   - Use `product_id` in body
   - Copy `offer.id` to `offer_id` variable

2. **Get Offers** → `GET /api/offers/`
   - View all offers for logged-in user

3. **Accept/Reject/Counter Offer** → Use respective endpoints

### Step 4: Chat

1. **Get Conversations** → `GET /api/chat/conversations/`
   - Get list of conversations
   - Copy `conversationId` to `conversation_id` variable

2. **Get Messages** → `GET /api/chat/conversations/{conversation_id}/messages/`
   - View messages in a conversation

3. **Send Message** → `POST /api/chat/send/`
   - Send text message
   - Can include `offerId` to send offer in chat

4. **Upload File** → `POST /api/chat/upload/`
   - Upload image/file for chat
   - Use form-data with file field

### Step 5: Payments

1. **Checkout** → `POST /api/payment/checkout/`
   - Create order from offer or cart
   - Copy `orderId` to `order_id` variable

2. **Process Payment** → `POST /api/payment/process/`
   - Process payment via Moyasar
   - Requires `tokenId` from Moyasar frontend integration

### Step 6: Notifications

1. **Create Notification (Admin)** → `POST /api/notifications/admin/create/`
   - Admin creates notification
   - Copy `notification.id` to `notification_id`

2. **Send Notification (Admin)** → `POST /api/notifications/admin/{notification_id}/send/`
   - Sends notification to target audience
   - **Real-time delivery via WebSocket** (see below)

3. **Get Notifications** → `GET /api/notifications/`
   - User views their notifications

## 🔌 Testing WebSockets (Chat & Notifications)

**Note:** Postman supports WebSockets in newer versions. If you don't have WebSocket support, use alternative methods below.

### Method 1: Postman WebSocket (Recommended)

1. In Postman, click **New** → **WebSocket Request**
2. Enter WebSocket URL:

**For Chat:**
```
ws://localhost:8000/ws/chat/{conversation_id}/?token={user_token}
```

**For Notifications:**
```
ws://localhost:8000/ws/notifications/{user_id}/?token={user_token}
```

3. Click **Connect**
4. Send messages in JSON format:

**Chat Message:**
```json
{
  "type": "chat_message",
  "senderId": "user_id",
  "receiverId": "receiver_id",
  "text": "Hello!",
  "conversationId": "conversation_id"
}
```

**Receive Messages:**
- Messages will appear in the response panel
- Format: `{"type": "chat_message", "message": {...}}`

### Method 2: Browser Console (Alternative)

If Postman doesn't support WebSockets, use browser console:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Run this code:

```javascript
// Chat WebSocket
const conversationId = 'YOUR_CONVERSATION_ID';
const token = 'YOUR_JWT_TOKEN';

const chatSocket = new WebSocket(
  `ws://localhost:8000/ws/chat/${conversationId}/?token=${token}`
);

chatSocket.onopen = () => console.log('Connected to chat');
chatSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Message received:', data);
};

// Send message
chatSocket.send(JSON.stringify({
  type: 'chat_message',
  senderId: 'user_id',
  receiverId: 'receiver_id',
  text: 'Hello from browser!',
  conversationId: conversationId
}));

// Notification WebSocket
const userId = 'YOUR_USER_ID';
const notifSocket = new WebSocket(
  `ws://localhost:8000/ws/notifications/${userId}/?token=${token}`
);

notifSocket.onopen = () => console.log('Connected to notifications');
notifSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Notification received:', data);
  // Show popup notification
  alert(`New Notification: ${data.notification.title}`);
};
```

### Method 3: wscat (Command Line)

Install wscat:
```bash
npm install -g wscat
```

Connect:
```bash
wscat -c "ws://localhost:8000/ws/chat/conversation_id/?token=YOUR_TOKEN"
```

## 📋 Testing Checklist

### Authentication ✅
- [ ] Admin signup
- [ ] Admin login
- [ ] User signup
- [ ] User login
- [ ] Affiliate signup
- [ ] Affiliate login
- [ ] Get profile
- [ ] Update profile

### Products ✅
- [ ] Get products (with filters)
- [ ] Get featured products
- [ ] Get trending products
- [ ] Get product detail
- [ ] Create product
- [ ] Update product
- [ ] Delete product
- [ ] Save/Unsave product

### Offers ✅
- [ ] Create offer
- [ ] Get offers
- [ ] Accept offer
- [ ] Reject offer
- [ ] Counter offer

### Chat ✅
- [ ] Get conversations
- [ ] Get messages
- [ ] Send message
- [ ] Send message with offer
- [ ] Upload file
- [ ] **WebSocket real-time chat** (test separately)

### Payments ✅
- [ ] Checkout
- [ ] Process payment
- [ ] Payment webhook

### Admin Dashboard ✅
- [ ] Dashboard stats
- [ ] Revenue trends
- [ ] Get users
- [ ] Suspend user
- [ ] Get listings
- [ ] Approve listing
- [ ] Get transactions
- [ ] Get disputes
- [ ] Update dispute
- [ ] Fee settings

### Notifications ✅
- [ ] Get notifications
- [ ] Mark as read
- [ ] Create notification (admin)
- [ ] Send notification (admin)
- [ ] **WebSocket real-time notifications** (test separately)

## 🎯 Quick Test Scenarios

### Scenario 1: Complete Purchase Flow
1. User signup → Login → Get token
2. Create product → Get product_id
3. Create offer → Get offer_id
4. Accept offer
5. Checkout → Get order_id
6. Process payment

### Scenario 2: Chat with Offer
1. User A creates product
2. User B creates offer on product
3. User B sends message with offerId
4. User A receives message (via WebSocket)
5. User A accepts offer
6. User B proceeds to checkout

### Scenario 3: Admin Notification
1. Admin creates notification
2. Admin sends notification to "all" users
3. Users receive notification via WebSocket (real-time popup)
4. Users can view notifications via API

## 🔍 Troubleshooting

**Issue:** 401 Unauthorized
- **Solution:** Check if token is set correctly in variables
- Make sure Authorization header has format: `Bearer {token}`

**Issue:** 404 Not Found
- **Solution:** Check if server is running on `http://localhost:8000`
- Verify endpoint URL is correct

**Issue:** WebSocket connection fails
- **Solution:** Make sure Redis is running (`redis-cli ping`)
- Check if using ASGI server (daphne), not just runserver

**Issue:** CORS errors
- **Solution:** Check CORS settings in `settings.py`
- Add your frontend URL to `CORS_ALLOWED_ORIGINS`

## 📝 Notes

- All endpoints requiring authentication need `Authorization: Bearer {token}` header
- WebSocket URLs use `ws://` not `http://`
- Tokens expire based on `JWT_EXPIRES_IN` setting (default: 1 day)
- For production, change `base_url` to your production domain

---

**Happy Testing! 🚀**

