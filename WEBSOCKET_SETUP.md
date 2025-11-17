# WebSocket Setup for Real-time Chat and Notifications

## ✅ What You DON'T Need

**You don't need any additional API keys, tokens, or external services for
WebSockets!**

The WebSocket implementation is **self-contained** and uses:

- **Django Channels** (already installed)
- **Redis** (local server - you just need to install and run it)
- **No external services or API keys required**

## 📋 What You DO Need

### 1. Install Redis

Redis is a lightweight in-memory database used for WebSocket message routing.

#### Windows:

**Option 1: Download Redis for Windows**

- Download from: https://github.com/microsoftarchive/redis/releases
- Extract and run `redis-server.exe`

**Option 2: Use WSL (Windows Subsystem for Linux)**

```bash
wsl
sudo apt-get update
sudo apt-get install redis-server
redis-server
```

**Option 3: Use Docker (Recommended)**

```bash
docker run -d -p 6379:6379 redis
```

#### Linux:

```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis  # Auto-start on boot
```

#### Mac:

```bash
brew install redis
brew services start redis
```

### 2. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

If you get "command not found", Redis is not installed or not in your PATH.

### 3. That's It! 🎉

Once Redis is running, your WebSockets will work automatically. The backend is
already configured to use Redis on `127.0.0.1:6379` (default).

## 🔌 How It Works

### Chat WebSocket

- **URL**: `ws://localhost:8000/ws/chat/<conversation_id>/`
- **Purpose**: Real-time messaging between users
- **Authentication**: JWT token in query parameter

### Notification WebSocket

- **URL**: `ws://localhost:8000/ws/notifications/<user_id>/`
- **Purpose**: Real-time notification delivery
- **Authentication**: JWT token in query parameter

## 🚀 Testing WebSockets

### Start Redis:

```bash
redis-server
```

### Start Django Server (with WebSocket support):

```bash
daphne dolabb_backend.asgi:application
# Or
python manage.py runserver  # (for development)
```

### Test in Browser Console:

```javascript
// Chat WebSocket
const chatSocket = new WebSocket(
  'ws://localhost:8000/ws/chat/conversation_id/?token=YOUR_JWT_TOKEN'
);

chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  console.log('Message:', data);
};

// Send message
chatSocket.send(
  JSON.stringify({
    type: 'chat_message',
    senderId: 'user_id',
    receiverId: 'receiver_id',
    text: 'Hello!',
  })
);
```

## 📝 Summary

**For Real-time Chat and Notifications:**

- ✅ **No API keys needed**
- ✅ **No external services needed**
- ✅ **Just install and run Redis locally**
- ✅ **Everything else is already configured!**

The WebSocket infrastructure is **100% self-contained** in your Django backend.
Redis is just used as a message broker between WebSocket connections - it's
free, lightweight, and runs locally on your machine.

## 🆘 Troubleshooting

**Problem**: WebSocket connection fails **Solution**: Make sure Redis is running
(`redis-cli ping` should return `PONG`)

**Problem**: "Connection refused" error **Solution**: Check Redis is running on
port 6379 (default)

**Problem**: Messages not being delivered **Solution**: Verify you're using
`daphne` or ASGI server, not just `runserver` for production

---

**That's all you need!** Just install Redis and you're good to go! 🚀
