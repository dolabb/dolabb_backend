# 🔌 WebSocket on Render Free Tier - Complete Guide

## ⚠️ Free Tier Limitations for WebSockets

### Critical Issues:

1. **Service Sleep:**
   - Free tier services **sleep after 15 minutes of inactivity**
   - When service sleeps, **all WebSocket connections are dropped**
   - Clients must reconnect after service wakes up
   - **Wake-up time: 30-60 seconds**

2. **Connection Reliability:**
   - Connections may drop unexpectedly
   - No guarantee of persistent connections
   - Reconnection required frequently

3. **Performance:**
   - Slower WebSocket performance
   - Higher latency
   - Limited concurrent connections

---

## ✅ What You're Using (Free Tier)

### Current Setup:

1. **Render Web Service (Free Tier)**
   - Django backend
   - Sleeps after 15 minutes
   - Limited resources

2. **Upstash Redis (Free Tier)**
   - 25MB storage limit
   - Single instance
   - Good for development/testing

### Configuration:

**Start Command (Current):**
```bash
gunicorn dolabb_backend.wsgi:application --bind 0.0.0.0:$PORT
```

**Start Command (For WebSockets):**
```bash
daphne -b 0.0.0.0 -p $PORT dolabb_backend.asgi:application
```

**Redis Connection:**
```
REDIS_URL=rediss://default:AWi-AAIncDIzYjhjMWRhMzg1MmU0MjIwYmRjMzY4MGM3OTQ1NTNiYXAyMjY4MTQ@communal-wombat-26814.upstash.io:6379
```

---

## 🔧 Setup Steps for WebSockets

### Step 1: Update Start Command in Render

1. Go to **Render Dashboard**
2. **Your Web Service → Settings**
3. Find **"Start Command"**
4. Change to:
   ```
   daphne -b 0.0.0.0 -p $PORT dolabb_backend.asgi:application
   ```
5. **Save Changes**
6. Wait for restart (1-2 minutes)

### Step 2: Verify Redis Connection

Check in Render → Environment:
- `REDIS_URL` is set correctly
- Upstash Redis is accessible

### Step 3: Test WebSocket Connection

**WebSocket URL:**
```
wss://dolabb-backend.onrender.com/ws/chat/{conversation_id}/
```

**Test in Browser Console:**
```javascript
const ws = new WebSocket('wss://dolabb-backend.onrender.com/ws/chat/691c7f09e8c4f33957183a48/');
ws.onopen = () => console.log('✅ Connected!');
ws.onerror = (e) => console.error('❌ Error:', e);
```

---

## 🎯 Free Tier WebSocket Behavior

### What Works:
✅ WebSocket connections can be established
✅ Messages can be sent/received
✅ Real-time features work when service is active

### What Doesn't Work Well:
❌ Connections drop when service sleeps
❌ 30-60s delay on first connection after sleep
❌ Unreliable for production use
❌ Poor user experience with frequent disconnects

---

## 💡 Workarounds for Free Tier

### Option 1: Keep Service Active (Recommended)

**Use Uptime Monitoring:**
- Services like **UptimeRobot** (free)
- Ping your service every 10 minutes
- Prevents service from sleeping
- **Cost:** Free

**Setup:**
1. Sign up at https://uptimerobot.com
2. Add monitor for: `https://dolabb-backend.onrender.com/`
3. Set interval: 5 minutes
4. Service stays awake!

### Option 2: Implement Reconnection Logic

**Frontend Code:**
```javascript
let ws;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
    ws = new WebSocket('wss://dolabb-backend.onrender.com/ws/chat/conversation_id/');
    
    ws.onopen = () => {
        console.log('Connected');
        reconnectAttempts = 0;
    };
    
    ws.onclose = () => {
        console.log('Disconnected, reconnecting...');
        if (reconnectAttempts < maxReconnectAttempts) {
            setTimeout(connectWebSocket, 5000);
            reconnectAttempts++;
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

connectWebSocket();
```

### Option 3: Use HTTP Polling as Fallback

If WebSocket fails, fall back to HTTP polling:
```javascript
// Poll for new messages every 5 seconds
setInterval(() => {
    fetch('/api/chat/conversations/conversation_id/messages/')
        .then(res => res.json())
        .then(data => {
            // Update UI with new messages
        });
}, 5000);
```

---

## 📊 Free Tier vs Paid Tier Comparison

| Feature | Free Tier | Starter ($7/mo) |
|---------|-----------|----------------|
| **Service Sleep** | ❌ 15 min inactivity | ✅ Always on |
| **WebSocket Reliability** | ⚠️ Drops on sleep | ✅ Persistent |
| **Wake-up Time** | ❌ 30-60 seconds | ✅ Instant |
| **Custom Domain** | ❌ No | ✅ Yes |
| **Performance** | ⚠️ Limited | ✅ Better |
| **Suitable For** | Development | Production |

---

## 🎯 Recommendations

### For Development/Testing:
✅ **Free Tier + UptimeRobot**
- Use free tier
- Set up UptimeRobot to keep service awake
- Good for testing WebSocket features
- **Cost:** $0/month

### For Production:
💼 **Upgrade to Starter Plan ($7/month)**
- No sleep = reliable WebSockets
- Better user experience
- Production-ready
- **Cost:** $7/month

### For High Traffic:
🚀 **Standard Plan ($25/month)**
- Better performance
- More resources
- Auto-scaling
- **Cost:** $25/month

---

## 🔍 Testing WebSocket on Free Tier

### Test Connection:
```javascript
const ws = new WebSocket('wss://dolabb-backend.onrender.com/ws/chat/691c7f09e8c4f33957183a48/');

ws.onopen = () => {
    console.log('✅ Connected!');
    // Send test message
    ws.send(JSON.stringify({
        type: 'chat_message',
        senderId: '6919de9c20bb75f898ef5005',
        receiverId: '6919de9c20bb75f898ef5005',
        text: 'Test from free tier',
        attachments: [],
        offerId: null,
        productId: null
    }));
};

ws.onmessage = (event) => {
    console.log('📨 Received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
    console.error('❌ Error:', error);
};

ws.onclose = () => {
    console.log('🔌 Disconnected - Service may have slept');
};
```

### Expected Behavior:
- ✅ Works when service is active
- ⚠️ Drops when service sleeps
- ⚠️ Takes 30-60s to reconnect after sleep

---

## ✅ Checklist

- [ ] Start command updated to Daphne
- [ ] Redis connection verified
- [ ] WebSocket endpoint tested
- [ ] UptimeRobot set up (optional, for free tier)
- [ ] Reconnection logic implemented (frontend)
- [ ] Error handling added
- [ ] User notifications for connection status

---

## 🚀 Upgrade Path

If you decide to upgrade:

1. **No code changes needed**
2. **Just change plan in Render**
3. **Update start command to Daphne**
4. **Test WebSocket connections**
5. **Enjoy reliable real-time features!**

**Upgrade Cost:** $7/month (Starter Plan)
**Benefit:** No sleep, reliable WebSockets, better UX

---

**Bottom Line:** Free tier works for development, but for production WebSockets, **upgrade to Starter Plan ($7/month) or use UptimeRobot to keep service awake.**

