# Dolabb Backend Setup Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Installation & Setup](#installation--setup)
3. [Environment Configuration](#environment-configuration)
4. [WebSockets Setup](#websockets-setup)
5. [Moyasar Payment Gateway Setup](#moyasar-payment-gateway-setup)
6. [Running the Server](#running-the-server)
7. [API Documentation](#api-documentation)

---

## Project Overview

This is a Django REST Framework backend for the Dolabb marketplace platform. It supports:
- **User Types**: Admin, Buyers, Sellers, Affiliates
- **Features**: Product management, Chat system, Offers, Payments, Notifications
- **Database**: MongoDB (using mongoengine)
- **Real-time**: WebSockets for chat and notifications
- **Payment**: Moyasar payment gateway integration

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (Atlas or local)
- Redis (for WebSockets)
- Virtual environment (recommended)

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Database Setup

The project uses MongoDB. The connection string is configured in `.env` file:
```
MONGODB_CONNECTION_STRING=mongodb+srv://dolabb_admin:Farad2025%24@cluster0.0imvu6l.mongodb.net/dolabb_db?retryWrites=true&w=majority
```

MongoDB will automatically create collections when models are first used.

---

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Resend (email OTP)
RESEND_API_KEY=re_GpJeG6m2_7XrfrArCDzQDSioMid4r4a74
RESEND_FROM_EMAIL=onboarding@resend.dev

# MongoDB
MONGODB_CONNECTION_STRING=mongodb+srv://dolabb_admin:Farad2025%24@cluster0.0imvu6l.mongodb.net/dolabb_db?retryWrites=true&w=majority

# JWT
SECRET_KEY=your_jwt_secret_here
JWT_EXPIRES_IN=1d
OTP_EXPIRY_SECONDS=300
PAGE_DEFAULT_LIMIT=10

# Moyasar Payment Gateway
MOYASAR_PUBLIC_KEY=your_moyasar_public_key
MOYASAR_SECRET_KEY=your_moyasar_secret_key

# Redis (for WebSockets)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

---

## WebSockets Setup

### Overview
The backend uses Django Channels for real-time WebSocket communication. WebSockets are used for:
1. **Chat System**: Real-time messaging between buyers and sellers
2. **Notifications**: Instant notification delivery when admin sends notifications

### Requirements

#### 1. Install Redis

**Windows:**
- Download Redis from: https://github.com/microsoftarchive/redis/releases
- Or use WSL (Windows Subsystem for Linux)
- Or use Docker: `docker run -d -p 6379:6379 redis`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

#### 2. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

### WebSocket Endpoints

#### Chat WebSocket
- **URL**: `ws://localhost:8000/ws/chat/<conversation_id>/`
- **Purpose**: Real-time chat messaging
- **Authentication**: JWT token in query parameter or header

**Connection Example (JavaScript):**
```javascript
const conversationId = 'your_conversation_id';
const token = 'your_jwt_token';

const chatSocket = new WebSocket(
    `ws://localhost:8000/ws/chat/${conversationId}/?token=${token}`
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'chat_message') {
        console.log('New message:', data.message);
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

// Send message
chatSocket.send(JSON.stringify({
    type: 'chat_message',
    senderId: 'user_id',
    receiverId: 'receiver_id',
    text: 'Hello!',
    conversationId: conversationId
}));
```

#### Notification WebSocket
- **URL**: `ws://localhost:8000/ws/notifications/<user_id>/`
- **Purpose**: Real-time notification delivery
- **Authentication**: JWT token in query parameter or header

**Connection Example (JavaScript):**
```javascript
const userId = 'your_user_id';
const token = 'your_jwt_token';

const notificationSocket = new WebSocket(
    `ws://localhost:8000/ws/notifications/${userId}/?token=${token}`
);

notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'notification') {
        console.log('New notification:', data.notification);
        // Show popup notification
        showNotificationPopup(data.notification);
    }
};

notificationSocket.onclose = function(e) {
    console.error('Notification socket closed unexpectedly');
};
```

### WebSocket Message Format

#### Chat Messages
```json
{
    "type": "chat_message",
    "message": {
        "id": "message_id",
        "text": "Message text",
        "sender": "me" | "other",
        "timestamp": "2025-01-15T10:30:00Z",
        "attachments": ["url1", "url2"]
    }
}
```

#### Notifications
```json
{
    "type": "notification",
    "notification": {
        "id": "notification_id",
        "title": "Notification Title",
        "message": "Notification message",
        "type": "system_alert",
        "createdAt": "2025-01-15T10:30:00Z"
    }
}
```

### Testing WebSockets

You can test WebSockets using:
1. **Browser Console**: Use the JavaScript examples above
2. **Postman**: Supports WebSocket testing (newer versions)
3. **wscat** (Node.js tool):
   ```bash
   npm install -g wscat
   wscat -c ws://localhost:8000/ws/chat/conversation_id/
   ```

---

## Moyasar Payment Gateway Setup

### Overview
Moyasar is a payment gateway for Saudi Arabia. The backend integrates with Moyasar API to process payments.

### Step 1: Create Moyasar Account

1. Go to: https://moyasar.com
2. Sign up for an account
3. Complete business verification (if required)

### Step 2: Get API Keys

1. Log in to Moyasar Dashboard
2. Navigate to **Settings** > **API Keys**
3. You'll find:
   - **Public Key**: Used for frontend tokenization
   - **Secret Key**: Used for backend payment processing (keep secret!)

### Step 3: Configure Environment Variables

Add to your `.env` file:
```env
MOYASAR_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx
MOYASAR_SECRET_KEY=sk_test_xxxxxxxxxxxxx
```

### Step 4: Payment Flow

#### Frontend (Tokenization)
1. User enters card details
2. Frontend calls Moyasar tokenization API to create a token
3. Token is sent to backend for processing

**Example (JavaScript):**
```javascript
// Include Moyasar JS SDK
<script src="https://cdn.moyasar.com/moyasar.js"></script>

// Tokenize card
Moyasar.init({
    element: '.mysr-form',
    amount: 10000, // Amount in fils (100 SAR = 10000 fils)
    currency: 'SAR',
    description: 'Order #123',
    publishable_api_key: 'your_public_key',
    callback_url: 'https://yourdomain.com/payment/callback',
    methods: ['creditcard'],
    on_complete: function(payment) {
        // Send token to backend
        fetch('/api/payment/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({
                orderId: 'order_id',
                tokenId: payment.token,
                amount: payment.amount,
                description: payment.description
            })
        });
    }
});
```

#### Backend Processing
The backend receives the token and processes payment:

```python
# payments/services.py - Already implemented
payment, payment_data = MoyasarPaymentService.process_payment(
    order_id, 
    card_details=None, 
    token_id=token_id,
    amount=amount,
    description=description
)
```

### Step 5: Webhook Setup (Optional but Recommended)

Moyasar can send webhooks for payment status updates:

1. In Moyasar Dashboard, go to **Settings** > **Webhooks**
2. Add webhook URL: `https://yourdomain.com/api/payment/webhook/`
3. Select events: `payment.paid`, `payment.failed`

**Webhook Handler** (Already implemented in `payments/views.py`):
```python
@api_view(['POST'])
def payment_webhook(request):
    # Verify webhook signature
    # Update payment status
    # Update order status
```

### Step 6: Testing Payments

#### Test Cards (Sandbox Mode)
Moyasar provides test cards:
- **Success**: `4111111111111111`
- **3D Secure**: `4000000000000002`
- **Declined**: `4000000000000069`

**Test Card Details:**
- CVV: Any 3 digits
- Expiry: Any future date
- Name: Any name

### Payment API Endpoints

1. **Checkout**: `POST /api/payment/checkout/`
   - Creates order from cart/offer
   
2. **Process Payment**: `POST /api/payment/process/`
   - Processes payment via Moyasar
   
3. **Webhook**: `POST /api/payment/webhook/`
   - Receives payment status updates from Moyasar

### Payment Response Format

```json
{
    "success": true,
    "payment": {
        "id": "payment_id",
        "status": "completed",
        "amount": 100.00,
        "currency": "SAR",
        "source": {
            "type": "creditcard",
            "company": "visa",
            "name": "Cardholder Name",
            "number": "4111",
            "gateway_id": "gateway_id",
            "reference_number": "ref_number"
        },
        "order": {
            "id": "order_id",
            "orderNumber": "ORD-XXXXXXXXXX"
        }
    }
}
```

---

## Running the Server

### Development Mode

#### 1. Run Redis (if not running as service)
```bash
redis-server
```

#### 2. Run Django Development Server
```bash
python manage.py runserver
```

#### 3. Run with ASGI (for WebSockets)
```bash
daphne -b 0.0.0.0 -p 8000 dolabb_backend.asgi:application
```

Or using uvicorn:
```bash
uvicorn dolabb_backend.asgi:application --host 0.0.0.0 --port 8000
```

### Production Mode

1. Use **Gunicorn** for HTTP:
   ```bash
   pip install gunicorn
   gunicorn dolabb_backend.wsgi:application
   ```

2. Use **Daphne** for WebSockets:
   ```bash
   daphne -b 0.0.0.0 -p 8000 dolabb_backend.asgi:application
   ```

3. Or use **Nginx** as reverse proxy:
   ```nginx
   upstream django {
       server 127.0.0.1:8000;
   }
   
   upstream websocket {
       server 127.0.0.1:8001;
   }
   
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://django;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /ws/ {
           proxy_pass http://websocket;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

---

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
Most endpoints require JWT authentication:
```
Authorization: Bearer <jwt_token>
```

### Main Endpoints

#### Authentication
- `POST /api/auth/signup/` - User signup
- `POST /api/auth/login/` - User login
- `POST /api/auth/admin/login/` - Admin login
- `POST /api/auth/affiliate/signup/` - Affiliate signup

#### Products
- `GET /api/products/` - Get products (with filters)
- `GET /api/products/<id>/` - Get product details
- `POST /api/products/create/` - Create product
- `GET /api/products/featured/` - Get featured products
- `GET /api/products/trending/` - Get trending products

#### Chat
- `GET /api/chat/conversations/` - Get conversations
- `GET /api/chat/conversations/<id>/messages/` - Get messages
- `POST /api/chat/send/` - Send message

#### Offers
- `POST /api/offers/create/` - Create offer
- `GET /api/offers/` - Get offers
- `PUT /api/offers/<id>/accept/` - Accept offer
- `PUT /api/offers/<id>/reject/` - Reject offer
- `POST /api/offers/<id>/counter/` - Counter offer

#### Payments
- `POST /api/payment/checkout/` - Create checkout
- `POST /api/payment/process/` - Process payment
- `POST /api/payment/webhook/` - Payment webhook

#### Admin Dashboard
- `GET /api/admin/dashboard/stats/` - Dashboard statistics
- `GET /api/admin/users/` - Get all users
- `GET /api/admin/listings/` - Get all listings
- `GET /api/admin/transactions/` - Get transactions
- `GET /api/admin/disputes/` - Get disputes

#### Notifications
- `GET /api/notifications/` - Get user notifications
- `POST /api/notifications/admin/create/` - Create notification (admin)
- `POST /api/notifications/admin/<id>/send/` - Send notification (admin)

#### Affiliates
- `POST /api/affiliate/validate-code/` - Validate affiliate code
- `POST /api/affiliate/cashout/` - Request cashout
- `GET /api/affiliate/all/` - Get all affiliates (admin)

---

## Troubleshooting

### WebSocket Connection Issues

1. **Check Redis is running:**
   ```bash
   redis-cli ping
   ```

2. **Check CORS settings** in `settings.py`

3. **Verify ASGI application** is being used (not WSGI)

4. **Check firewall** allows WebSocket connections

### Payment Issues

1. **Verify API keys** are correct in `.env`

2. **Check Moyasar dashboard** for transaction logs

3. **Test with sandbox mode** first

4. **Verify webhook URL** is accessible

### MongoDB Connection Issues

1. **Check connection string** in `.env`

2. **Verify network access** to MongoDB Atlas (if using)

3. **Check IP whitelist** in MongoDB Atlas

---

## Additional Resources

- **Django Channels Documentation**: https://channels.readthedocs.io/
- **Moyasar Documentation**: https://moyasar.com/docs/
- **MongoEngine Documentation**: http://docs.mongoengine.org/
- **Django REST Framework**: https://www.django-rest-framework.org/

---

## Support

For issues or questions, please refer to the project documentation or contact the development team.

