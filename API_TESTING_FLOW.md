# 🔄 Complete API Testing Flow

## ✅ Tested Successfully!

All APIs are working on: `https://dolabb-backend.onrender.com/`

---

## 📋 Step-by-Step Flow

### Step 1: Login and Get Token

**Endpoint:** `POST /api/auth/login/`

**PowerShell Command:**
```powershell
$body = @{email="anaspirzada510@gmail.com"; password="Anasbuyer123@"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
$token = $response.token
$userId = $response.user.id
```

**Response:**
```json
{
    "success": true,
    "user": {
        "id": "6919de9c20bb75f898ef5005",
        "username": "Anas",
        "email": "anaspirzada510@gmail.com",
        ...
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Save:** `$token` and `$userId` for next steps

---

### Step 2: Send a Message (Creates Conversation)

**Endpoint:** `POST /api/chat/send/`

**PowerShell Command:**
```powershell
$headers = @{Authorization="Bearer $token"}
$body = @{
    senderId=$userId
    receiverId=$userId  # or another user ID
    text="Test message from terminal"
} | ConvertTo-Json

$sendResponse = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/chat/send/" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

**Response:**
```json
{
    "success": true,
    "message": {
        "id": "691c7f0be8c4f33957183a49",
        "text": "Test message from terminal",
        "timestamp": "2025-11-18T14:13:30.161614"
    }
}
```

---

### Step 3: Get Conversations (Extract conversation_id)

**Endpoint:** `GET /api/chat/conversations/`

**PowerShell Command:**
```powershell
$conversations = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/chat/conversations/" -Method GET -Headers $headers
$conversationId = $conversations.conversations[0].id
```

**Response:**
```json
{
    "success": true,
    "conversations": [
        {
            "id": "691c7f09e8c4f33957183a48",
            "conversationId": "691c7f09e8c4f33957183a48",
            "otherUser": {...},
            "lastMessage": "Test message from terminal",
            "lastMessageAt": "2025-11-18T14:13:31.578000",
            "unreadCount": "1"
        }
    ]
}
```

**Extract:** `conversation_id = "691c7f09e8c4f33957183a48"`

---

### Step 4: Get Messages for Conversation

**Endpoint:** `GET /api/chat/conversations/{conversation_id}/messages/`

**PowerShell Command:**
```powershell
$conversationId = "691c7f09e8c4f33957183a48"
$messages = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/chat/conversations/$conversationId/messages/" -Method GET -Headers $headers
```

**Response:**
```json
{
    "success": true,
    "messages": [
        {
            "id": "691c7f0be8c4f33957183a49",
            "text": "Test message from terminal",
            "sender": "me",
            "timestamp": "2025-11-18T14:13:30.161000",
            "attachments": []
        }
    ],
    "pagination": {
        "currentPage": 1,
        "totalPages": 1,
        "totalItems": 1
    }
}
```

---

## 🔌 WebSocket Testing with conversation_id

### WebSocket URL:
```
wss://dolabb-backend.onrender.com/ws/chat/{conversation_id}/
```

**Example:**
```
wss://dolabb-backend.onrender.com/ws/chat/691c7f09e8c4f33957183a48/
```

### Test in Browser Console:
```javascript
const conversationId = '691c7f09e8c4f33957183a48';
const ws = new WebSocket(`wss://dolabb-backend.onrender.com/ws/chat/${conversationId}/`);

ws.onopen = () => {
    console.log('✅ Connected to chat WebSocket!');
    
    // Send a message
    ws.send(JSON.stringify({
        type: 'chat_message',
        senderId: '6919de9c20bb75f898ef5005',
        receiverId: '6919de9c20bb75f898ef5005',
        text: 'Hello from WebSocket!',
        attachments: [],
        offerId: null,
        productId: null
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Received:', data);
};

ws.onerror = (error) => {
    console.error('❌ Error:', error);
};
```

---

## 📝 Complete PowerShell Script

```powershell
# Step 1: Login
$body = @{email="anaspirzada510@gmail.com"; password="Anasbuyer123@"} | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
$token = $loginResponse.token
$userId = $loginResponse.user.id
Write-Host "✅ Logged in. User ID: $userId"

# Step 2: Send Message
$headers = @{Authorization="Bearer $token"}
$messageBody = @{
    senderId=$userId
    receiverId=$userId
    text="Test message from PowerShell script"
} | ConvertTo-Json
$sendResponse = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/chat/send/" -Method POST -Headers $headers -Body $messageBody -ContentType "application/json"
Write-Host "✅ Message sent. Message ID: $($sendResponse.message.id)"

# Step 3: Get Conversations
$conversations = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/chat/conversations/" -Method GET -Headers $headers
$conversationId = $conversations.conversations[0].id
Write-Host "✅ Found conversation. Conversation ID: $conversationId"

# Step 4: Get Messages
$messages = Invoke-RestMethod -Uri "https://dolabb-backend.onrender.com/api/chat/conversations/$conversationId/messages/" -Method GET -Headers $headers
Write-Host "✅ Retrieved $($messages.messages.Count) messages"
Write-Host "`n📋 Conversation ID for WebSocket: $conversationId"
Write-Host "🔌 WebSocket URL: wss://dolabb-backend.onrender.com/ws/chat/$conversationId/"
```

---

## 🎯 Summary

**Your conversation_id:** `691c7f09e8c4f33957183a48`

**WebSocket URL:**
```
wss://dolabb-backend.onrender.com/ws/chat/691c7f09e8c4f33957183a48/
```

**User ID:** `6919de9c20bb75f898ef5005`

---

## ✅ All APIs Working!

- ✅ Login API
- ✅ Send Message API
- ✅ Get Conversations API
- ✅ Get Messages API

**Next:** Test WebSocket connection using the conversation_id above!

