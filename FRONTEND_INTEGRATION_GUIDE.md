# Frontend Integration Guide - Unread Messages Indicator

## API Endpoint

**Endpoint:** `GET /api/chat/unread-status/`

**Authentication:** Required (Bearer token)

**Response:**
```json
{
  "success": true,
  "hasUnreadMessages": true,
  "totalUnreadCount": 5
}
```

**Response Fields:**
- `hasUnreadMessages` (boolean): `true` if there are any unread messages, `false` otherwise
- `totalUnreadCount` (number): Total count of unread messages across all conversations

---

## Frontend Integration Examples

### React/Next.js Example

#### 1. Create a Custom Hook (Recommended)

```typescript
// hooks/useUnreadMessages.ts
import { useState, useEffect } from 'react';

interface UnreadStatus {
  hasUnreadMessages: boolean;
  totalUnreadCount: number;
}

export const useUnreadMessages = (pollInterval = 30000) => {
  const [unreadStatus, setUnreadStatus] = useState<UnreadStatus>({
    hasUnreadMessages: false,
    totalUnreadCount: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUnreadStatus = async () => {
    try {
      const token = localStorage.getItem('token'); // or your auth method
      const response = await fetch('/api/chat/unread-status/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch unread status');
      }

      const data = await response.json();
      if (data.success) {
        setUnreadStatus({
          hasUnreadMessages: data.hasUnreadMessages,
          totalUnreadCount: data.totalUnreadCount,
        });
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error fetching unread status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch immediately
    fetchUnreadStatus();

    // Set up polling if interval is provided
    let intervalId: NodeJS.Timeout | null = null;
    if (pollInterval > 0) {
      intervalId = setInterval(fetchUnreadStatus, pollInterval);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [pollInterval]);

  return { unreadStatus, loading, error, refetch: fetchUnreadStatus };
};
```

#### 2. Use in Messages Tab Component

```tsx
// components/MessagesTab.tsx
import { useUnreadMessages } from '@/hooks/useUnreadMessages';

export const MessagesTab = () => {
  const { unreadStatus } = useUnreadMessages(30000); // Poll every 30 seconds

  return (
    <div className="messages-tab">
      <div className="tab-header">
        <span>Messages</span>
        {/* Red indicator when there are unread messages */}
        {unreadStatus.hasUnreadMessages && (
          <span 
            className="unread-indicator"
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: 'red',
              display: 'inline-block',
              marginLeft: '8px',
            }}
            title={`${unreadStatus.totalUnreadCount} unread messages`}
          />
        )}
      </div>
      {/* Rest of your messages tab content */}
    </div>
  );
};
```

#### 3. Alternative: Simple Component with Manual Refresh

```tsx
// components/MessagesTab.tsx
import { useState, useEffect } from 'react';

export const MessagesTab = () => {
  const [hasUnread, setHasUnread] = useState(false);
  const [totalUnread, setTotalUnread] = useState(0);

  const checkUnreadMessages = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/chat/unread-status/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      
      if (data.success) {
        setHasUnread(data.hasUnreadMessages);
        setTotalUnread(data.totalUnreadCount);
      }
    } catch (error) {
      console.error('Error checking unread messages:', error);
    }
  };

  useEffect(() => {
    checkUnreadMessages();
    // Refresh when component mounts or when user navigates to messages
    const interval = setInterval(checkUnreadMessages, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="messages-tab">
      <span>Messages</span>
      {hasUnread && (
        <span 
          className="unread-dot"
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: 'red',
            display: 'inline-block',
            marginLeft: '8px',
          }}
        />
      )}
    </div>
  );
};
```

---

### Vue.js Example

```vue
<template>
  <div class="messages-tab">
    <span>Messages</span>
    <span 
      v-if="hasUnreadMessages"
      class="unread-indicator"
      :title="`${totalUnreadCount} unread messages`"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const hasUnreadMessages = ref(false);
const totalUnreadCount = ref(0);
let pollInterval = null;

const checkUnreadStatus = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/chat/unread-status/', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    const data = await response.json();
    
    if (data.success) {
      hasUnreadMessages.value = data.hasUnreadMessages;
      totalUnreadCount.value = data.totalUnreadCount;
    }
  } catch (error) {
    console.error('Error checking unread status:', error);
  }
};

onMounted(() => {
  checkUnreadStatus();
  pollInterval = setInterval(checkUnreadStatus, 30000); // Every 30 seconds
});

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval);
  }
});
</script>

<style scoped>
.unread-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: red;
  display: inline-block;
  margin-left: 8px;
}
</style>
```

---

### Vanilla JavaScript Example

```javascript
// messagesTab.js
class MessagesTab {
  constructor() {
    this.hasUnread = false;
    this.totalUnread = 0;
    this.pollInterval = null;
    this.init();
  }

  async checkUnreadStatus() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/chat/unread-status/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      
      if (data.success) {
        this.hasUnread = data.hasUnreadMessages;
        this.totalUnread = data.totalUnreadCount;
        this.updateIndicator();
      }
    } catch (error) {
      console.error('Error checking unread status:', error);
    }
  }

  updateIndicator() {
    const indicator = document.querySelector('.unread-indicator');
    if (this.hasUnread) {
      if (!indicator) {
        const span = document.createElement('span');
        span.className = 'unread-indicator';
        span.style.cssText = `
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: red;
          display: inline-block;
          margin-left: 8px;
        `;
        span.title = `${this.totalUnread} unread messages`;
        document.querySelector('.messages-tab').appendChild(span);
      }
    } else {
      if (indicator) {
        indicator.remove();
      }
    }
  }

  init() {
    this.checkUnreadStatus();
    this.pollInterval = setInterval(() => this.checkUnreadStatus(), 30000);
  }

  destroy() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  }
}

// Usage
const messagesTab = new MessagesTab();
```

---

## CSS Styling Options

### Option 1: Simple Red Dot
```css
.unread-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ff0000;
  display: inline-block;
  margin-left: 8px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

### Option 2: Badge with Count
```css
.unread-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  border-radius: 9px;
  background-color: #ff0000;
  color: white;
  font-size: 11px;
  font-weight: bold;
  margin-left: 8px;
}
```

### Option 3: Red Border/Outline
```css
.messages-tab {
  position: relative;
}

.messages-tab.has-unread::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ff0000;
}
```

---

## Integration with WebSocket (Real-time Updates)

If you're using WebSocket for real-time messages, you can update the indicator when new messages arrive:

```typescript
// In your WebSocket handler
websocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'new_message' && !data.isSender) {
    // New message received, update unread status
    fetchUnreadStatus(); // Call your fetch function
  }
};
```

---

## Best Practices

1. **Polling Interval**: 
   - Use 30-60 seconds for polling to balance between real-time updates and server load
   - Consider using WebSocket for real-time updates instead of frequent polling

2. **Error Handling**: 
   - Always handle errors gracefully
   - Don't show the indicator if the API call fails

3. **Performance**: 
   - Clear intervals when component unmounts
   - Consider debouncing if user navigates frequently

4. **User Experience**: 
   - Show a subtle indicator (small red dot) rather than blocking UI
   - Optionally show the count in a badge
   - Clear the indicator when user opens messages tab

5. **Refresh Strategy**:
   - Fetch immediately when component mounts
   - Refresh when user returns to the app (focus event)
   - Refresh after sending/receiving a message

---

## Testing

Test the endpoint:
```bash
curl -X GET "https://your-api-domain.com/api/chat/unread-status/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "success": true,
  "hasUnreadMessages": true,
  "totalUnreadCount": 3
}
```

---

## Notes

- The endpoint is lightweight and optimized for frequent polling
- It only queries conversation metadata, not individual messages
- The `hasUnreadMessages` boolean is perfect for showing/hiding the red indicator
- The `totalUnreadCount` can be used to show a badge with the number

