# 🚀 Deployment Guide for GoDaddy VPS

This guide will help you deploy your Django backend to a GoDaddy VPS server with
WebSocket support for chat and notifications.

## 📋 Prerequisites

- GoDaddy VPS with Ubuntu/Debian Linux
- SSH access to your VPS
- Domain name (optional, you can use IP address)
- MongoDB connection string
- All API keys (Resend, Moyasar, etc.)

## 🔧 Step 1: Initial Server Setup

### 1.1 Connect to your VPS

```bash
ssh root@your_server_ip
# or
ssh your_username@your_server_ip
```

### 1.2 Update system packages

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 1.3 Install required system packages

```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    redis-server \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev
```

### 1.4 Start and enable Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

## 📦 Step 2: Upload Your Code

### Option A: Using Git (Recommended)

```bash
# On your VPS
cd /var/www
sudo git clone https://github.com/yourusername/your-repo.git dolabb_backend
sudo chown -R $USER:$USER /var/www/dolabb_backend
cd dolabb_backend
```

### Option B: Using SCP (from your local machine)

```bash
# From your local machine
scp -r /path/to/your/backend root@your_server_ip:/var/www/dolabb_backend
```

### Option C: Using SFTP Client

Use FileZilla, WinSCP, or any SFTP client to upload your project folder to
`/var/www/dolabb_backend`

## 🔐 Step 3: Configure Environment Variables

### 3.1 Create .env file

```bash
cd /var/www/dolabb_backend
nano .env
```

### 3.2 Add your production environment variables

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your_domain.com,www.your_domain.com,your_server_ip
DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production

# MongoDB
MONGODB_CONNECTION_STRING=your_mongodb_connection_string

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Email (Resend)
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=noreply@yourdomain.com
OTP_EXPIRY_SECONDS=300

# Moyasar Payment
MOYASAR_SECRET_KEY=your_moyasar_secret_key
MOYASAR_PUBLISHABLE_KEY=your_moyasar_publishable_key

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# CORS (Update with your frontend URLs)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Pagination
PAGE_DEFAULT_LIMIT=10
```

**Important:** Generate a new SECRET_KEY for production:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🐍 Step 4: Set Up Python Environment

### 4.1 Create virtual environment

```bash
cd /var/www/dolabb_backend
python3 -m venv venv
source venv/bin/activate
```

### 4.2 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Create necessary directories

```bash
mkdir -p logs
mkdir -p media/uploads/profiles
mkdir -p staticfiles
```

### 4.4 Collect static files

```bash
export DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production
python manage.py collectstatic --noinput
```

## ⚙️ Step 5: Configure Systemd Services

### 5.1 Create Gunicorn service

```bash
sudo nano /etc/systemd/system/dolabb-backend.service
```

Paste the following (update paths):

```ini
[Unit]
Description=Django Backend Gunicorn daemon
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/dolabb_backend
Environment="PATH=/var/www/dolabb_backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production"
ExecStart=/var/www/dolabb_backend/venv/bin/gunicorn \
    --config /var/www/dolabb_backend/gunicorn_config.py \
    dolabb_backend.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 5.2 Create Daphne service (for WebSockets)

```bash
sudo nano /etc/systemd/system/dolabb-daphne.service
```

Paste the following (update paths):

```ini
[Unit]
Description=Django Channels Daphne ASGI server
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/dolabb_backend
Environment="PATH=/var/www/dolabb_backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production"
ExecStart=/var/www/dolabb_backend/venv/bin/daphne \
    -b 127.0.0.1 \
    -p 8001 \
    dolabb_backend.asgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 5.3 Update file permissions

```bash
sudo chown -R www-data:www-data /var/www/dolabb_backend
sudo chmod -R 755 /var/www/dolabb_backend
```

### 5.4 Enable and start services

```bash
sudo systemctl daemon-reload
sudo systemctl enable dolabb-backend
sudo systemctl enable dolabb-daphne
sudo systemctl start dolabb-backend
sudo systemctl start dolabb-daphne

# Check status
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne
```

## 🌐 Step 6: Configure Nginx

### 6.1 Create Nginx configuration

```bash
sudo nano /etc/nginx/sites-available/dolabb_backend
```

Paste the following (update domain and paths):

```nginx
upstream django {
    server 127.0.0.1:8000;
}

upstream daphne {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name your_domain.com www.your_domain.com your_server_ip;

    client_max_body_size 10M;

    access_log /var/log/nginx/dolabb_access.log;
    error_log /var/log/nginx/dolabb_error.log;

    # Static files
    location /static/ {
        alias /var/www/dolabb_backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/dolabb_backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # WebSocket connections (Chat and Notifications)
    location /ws/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Django application
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 6.2 Enable the site

```bash
sudo ln -s /etc/nginx/sites-available/dolabb_backend /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

## 🔒 Step 7: Configure Firewall (Optional but Recommended)

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS (if using SSL)
sudo ufw enable
```

## ✅ Step 8: Verify Deployment

### 8.1 Check services are running

```bash
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne
sudo systemctl status nginx
sudo systemctl status redis-server
```

### 8.2 Test API endpoints

```bash
# Test HTTP endpoint
curl http://your_domain.com/api/products/

# Test WebSocket (from your local machine or browser console)
# ws://your_domain.com/ws/chat/conversation_id/?token=your_jwt_token
```

### 8.3 Check logs if there are issues

```bash
# Django logs
tail -f /var/www/dolabb_backend/logs/django.log

# Gunicorn logs
tail -f /var/www/dolabb_backend/logs/gunicorn_error.log

# Nginx logs
sudo tail -f /var/log/nginx/dolabb_error.log

# Service logs
sudo journalctl -u dolabb-backend -f
sudo journalctl -u dolabb-daphne -f
```

## 🔄 Step 9: Update Deployment (When Making Changes)

```bash
cd /var/www/dolabb_backend
source venv/bin/activate

# Pull latest code (if using Git)
git pull

# Install new dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart dolabb-backend
sudo systemctl restart dolabb-daphne
```

## 🔐 Step 10: SSL Certificate (Optional but Recommended)

If you have a domain, set up SSL with Let's Encrypt:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Then update your Nginx config to use HTTPS and update CORS settings in `.env`.

## 📱 Testing WebSockets

### Test Chat WebSocket

```javascript
// From browser console or your frontend
const conversationId = 'your_conversation_id';
const token = 'your_jwt_token';

const chatSocket = new WebSocket(
  `ws://your_domain.com/ws/chat/${conversationId}/?token=${token}`
);

chatSocket.onopen = () => console.log('Chat WebSocket connected');
chatSocket.onmessage = e => console.log('Message:', JSON.parse(e.data));
chatSocket.onerror = e => console.error('WebSocket error:', e);
```

### Test Notification WebSocket

```javascript
const userId = 'your_user_id';
const token = 'your_jwt_token';

const notificationSocket = new WebSocket(
  `ws://your_domain.com/ws/notifications/${userId}/?token=${token}`
);

notificationSocket.onopen = () =>
  console.log('Notification WebSocket connected');
notificationSocket.onmessage = e =>
  console.log('Notification:', JSON.parse(e.data));
```

## 🐛 Troubleshooting

### Services won't start

1. Check logs: `sudo journalctl -u dolabb-backend -n 50`
2. Verify .env file exists and has all required variables
3. Check file permissions:
   `sudo chown -R www-data:www-data /var/www/dolabb_backend`

### WebSockets not working

1. Verify Redis is running: `redis-cli ping`
2. Check Daphne service: `sudo systemctl status dolabb-daphne`
3. Check Nginx WebSocket configuration
4. Test WebSocket connection directly:
   `wscat -c ws://your_domain.com/ws/chat/test/?token=test`

### 502 Bad Gateway

1. Check if Gunicorn is running: `sudo systemctl status dolabb-backend`
2. Check if port 8000 is in use: `sudo netstat -tlnp | grep 8000`
3. Check Nginx error logs: `sudo tail -f /var/log/nginx/dolabb_error.log`

### Static files not loading

1. Run collectstatic: `python manage.py collectstatic --noinput`
2. Check Nginx static file path matches your project
3. Check file permissions

## 📞 Support

If you encounter issues:

1. Check all service logs
2. Verify all environment variables are set
3. Ensure Redis is running
4. Check firewall settings
5. Verify MongoDB connection

---

**Your backend should now be live at:** `http://your_domain.com` or
`http://your_server_ip`

**WebSocket URLs:**

- Chat: `ws://your_domain.com/ws/chat/<conversation_id>/?token=<jwt_token>`
- Notifications:
  `ws://your_domain.com/ws/notifications/<user_id>/?token=<jwt_token>`
