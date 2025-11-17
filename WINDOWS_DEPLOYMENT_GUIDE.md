# 🪟 Windows 11 to GoDaddy VPS Deployment Guide

Complete step-by-step guide to deploy your Django backend from Windows 11 to GoDaddy VPS.

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ GoDaddy VPS credentials (IP address, username, password or SSH key)
- ✅ Your project code ready on Windows
- ✅ MongoDB connection string
- ✅ All API keys (Resend, Moyasar, etc.)

## 🔧 Step 1: Install Required Tools on Windows

### 1.1 Install PuTTY (SSH Client)

1. Download PuTTY from: https://www.putty.org/
2. Or use Windows Terminal (built-in, recommended)

### 1.2 Install WinSCP (File Transfer)

1. Download WinSCP from: https://winscp.net/eng/download.php
2. Install with default settings

### 1.3 Install Git (Optional but Recommended)

1. Download Git from: https://git-scm.com/download/win
2. Install with default settings

---

## 🔐 Step 2: Connect to Your GoDaddy VPS

### Option A: Using Windows Terminal (Recommended)

1. **Open Windows Terminal** (Press `Win + X` and select "Windows Terminal" or search for it)

2. **Connect via SSH:**
   ```bash
   ssh root@your_server_ip
   # or
   ssh your_username@your_server_ip
   ```

3. **Enter your password** when prompted

4. **If first time connecting**, type `yes` to accept the host key

### Option B: Using PuTTY

1. **Open PuTTY**

2. **Enter connection details:**
   - Host Name (or IP address): `your_server_ip`
   - Port: `22`
   - Connection type: `SSH`
   - Click **Open**

3. **Enter credentials:**
   - Username: `root` (or your username)
   - Password: (enter your password)

---

## 📦 Step 3: Initial Server Setup

Once connected to your VPS, run these commands:

### 3.1 Update System Packages

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3.2 Install Required Software

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
    python3-dev \
    ufw
```

### 3.3 Start and Enable Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 3.4 Configure Firewall

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

---

## 📤 Step 4: Upload Your Code to VPS

### Option A: Using WinSCP (Easiest for Windows)

1. **Open WinSCP**

2. **Create New Session:**
   - File protocol: `SFTP`
   - Host name: `your_server_ip`
   - Port number: `22`
   - User name: `root` (or your username)
   - Password: (enter your password)
   - Click **Login**

3. **Navigate to destination:**
   - On the right side (server), navigate to `/var/www`
   - Create folder `dolabb_backend` if it doesn't exist

4. **Upload files:**
   - On the left side (your Windows PC), navigate to your project folder
   - Select all files and folders (Ctrl+A)
   - Drag and drop to `/var/www/dolabb_backend` on the server
   - Wait for upload to complete

### Option B: Using Git (If your code is in a repository)

1. **On your VPS (via SSH):**
   ```bash
   cd /var/www
   sudo git clone https://github.com/yourusername/your-repo.git dolabb_backend
   sudo chown -R $USER:$USER /var/www/dolabb_backend
   cd dolabb_backend
   ```

### Option C: Using SCP from Windows Terminal

1. **Open Windows Terminal** in your project directory

2. **Upload files:**
   ```bash
   scp -r * root@your_server_ip:/var/www/dolabb_backend/
   ```

---

## 🔐 Step 5: Configure Environment Variables

### 5.1 Create .env File on Server

1. **Connect to your VPS via SSH** (using Windows Terminal or PuTTY)

2. **Navigate to project directory:**
   ```bash
   cd /var/www/dolabb_backend
   ```

3. **Create .env file:**
   ```bash
   nano .env
   ```

4. **Add your production environment variables:**
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

5. **Save and exit:**
   - Press `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

6. **Generate SECRET_KEY:**
   ```bash
   python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Copy the output and replace `your-super-secret-key-here-generate-a-new-one` in `.env`

---

## 🐍 Step 6: Set Up Python Environment

### 6.1 Create Virtual Environment

```bash
cd /var/www/dolabb_backend
python3 -m venv venv
source venv/bin/activate
```

### 6.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3 Create Necessary Directories

```bash
mkdir -p logs
mkdir -p media/uploads/profiles
mkdir -p staticfiles
```

### 6.4 Collect Static Files

```bash
export DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production
python manage.py collectstatic --noinput
```

---

## ⚙️ Step 7: Configure Systemd Services

### 7.1 Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/dolabb-backend.service
```

**Paste the following (update paths if needed):**

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

**Save:** `Ctrl + X`, then `Y`, then `Enter`

### 7.2 Create Daphne Service (for WebSockets)

```bash
sudo nano /etc/systemd/system/dolabb-daphne.service
```

**Paste the following:**

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

**Save:** `Ctrl + X`, then `Y`, then `Enter`

### 7.3 Set File Permissions

```bash
sudo chown -R www-data:www-data /var/www/dolabb_backend
sudo chmod -R 755 /var/www/dolabb_backend
```

### 7.4 Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable dolabb-backend
sudo systemctl enable dolabb-daphne
sudo systemctl start dolabb-backend
sudo systemctl start dolabb-daphne
```

### 7.5 Check Service Status

```bash
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne
```

**Press `Q` to exit status view**

---

## 🌐 Step 8: Configure Nginx

### 8.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/dolabb_backend
```

**Paste the following (update domain and paths):**

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

**Important:** Replace:
- `your_domain.com` with your actual domain
- `your_server_ip` with your VPS IP address

**Save:** `Ctrl + X`, then `Y`, then `Enter`

### 8.2 Enable the Site

```bash
sudo ln -s /etc/nginx/sites-available/dolabb_backend /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
```

**If test is successful, reload Nginx:**
```bash
sudo systemctl reload nginx
```

---

## ✅ Step 9: Verify Deployment

### 9.1 Check All Services

```bash
# Check all services are running
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne
sudo systemctl status nginx
sudo systemctl status redis-server
```

### 9.2 Test API from Windows

**Open your browser on Windows and test:**
```
http://your_server_ip/api/products/
```

**Or use PowerShell/Command Prompt:**
```powershell
curl http://your_server_ip/api/products/
```

### 9.3 Check Logs (if there are issues)

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

**Press `Ctrl + C` to stop viewing logs**

---

## 🔄 Step 10: Update Code (When Making Changes)

### 10.1 Upload Updated Files

**Using WinSCP:**
1. Connect to your VPS
2. Navigate to `/var/www/dolabb_backend`
3. Upload only changed files

**Or using Git:**
```bash
cd /var/www/dolabb_backend
git pull
```

### 10.2 Restart Services

```bash
cd /var/www/dolabb_backend
source venv/bin/activate

# Install new dependencies (if any)
pip install -r requirements.txt

# Collect static files (if changed)
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart dolabb-backend
sudo systemctl restart dolabb-daphne
```

---

## 🔒 Step 11: SSL Certificate (Optional but Recommended)

If you have a domain name:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Then update your `.env` file:
- Set `CORS_ALLOWED_ORIGINS` to use `https://`
- Update `ALLOWED_HOSTS` if needed

---

## 📱 Testing WebSockets from Windows

### Test Chat WebSocket

**Create a test HTML file on Windows:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>Chat WebSocket Test</h1>
    <div id="messages"></div>
    <script>
        const conversationId = 'test_conversation';
        const token = 'your_jwt_token_here';
        
        const chatSocket = new WebSocket(
            `ws://your_server_ip/ws/chat/${conversationId}/?token=${token}`
        );
        
        chatSocket.onopen = () => {
            console.log('Chat WebSocket connected');
            document.getElementById('messages').innerHTML += '<p>Connected!</p>';
        };
        
        chatSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            console.log('Message:', data);
            document.getElementById('messages').innerHTML += `<p>${JSON.stringify(data)}</p>`;
        };
        
        chatSocket.onerror = (e) => {
            console.error('WebSocket error:', e);
            document.getElementById('messages').innerHTML += '<p>Error occurred</p>';
        };
        
        chatSocket.onclose = () => {
            console.log('WebSocket closed');
            document.getElementById('messages').innerHTML += '<p>Disconnected</p>';
        };
    </script>
</body>
</html>
```

Open this file in your browser to test.

---

## 🐛 Common Issues and Solutions

### Issue: Can't connect via SSH

**Solution:**
- Check if SSH is enabled on your VPS
- Verify IP address and credentials
- Check firewall settings on GoDaddy

### Issue: Permission denied errors

**Solution:**
```bash
sudo chown -R www-data:www-data /var/www/dolabb_backend
sudo chmod -R 755 /var/www/dolabb_backend
```

### Issue: Services won't start

**Solution:**
```bash
# Check logs
sudo journalctl -u dolabb-backend -n 50
sudo journalctl -u dolabb-daphne -n 50

# Verify .env file exists
ls -la /var/www/dolabb_backend/.env

# Check if Redis is running
redis-cli ping
```

### Issue: 502 Bad Gateway

**Solution:**
```bash
# Check if services are running
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne

# Check ports
sudo netstat -tlnp | grep 8000
sudo netstat -tlnp | grep 8001
```

### Issue: WebSockets not working

**Solution:**
```bash
# Verify Redis is running
redis-cli ping

# Check Daphne service
sudo systemctl status dolabb-daphne

# Check Nginx WebSocket config
sudo nginx -t
```

---

## 📞 Quick Reference Commands

```bash
# Connect to VPS
ssh root@your_server_ip

# Navigate to project
cd /var/www/dolabb_backend

# Activate virtual environment
source venv/bin/activate

# Check service status
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne
sudo systemctl status nginx
sudo systemctl status redis-server

# Restart services
sudo systemctl restart dolabb-backend
sudo systemctl restart dolabb-daphne
sudo systemctl reload nginx

# View logs
sudo journalctl -u dolabb-backend -f
sudo journalctl -u dolabb-daphne -f
tail -f /var/www/dolabb_backend/logs/django.log
```

---

## ✅ Deployment Checklist

- [ ] Connected to VPS via SSH
- [ ] Installed all required packages
- [ ] Redis is running
- [ ] Uploaded code to `/var/www/dolabb_backend`
- [ ] Created `.env` file with production values
- [ ] Created virtual environment and installed dependencies
- [ ] Collected static files
- [ ] Created and enabled systemd services
- [ ] Configured Nginx
- [ ] Tested API endpoints
- [ ] Tested WebSocket connections
- [ ] Set up SSL (if using domain)

---

**Your backend should now be live!** 🎉

**API URL:** `http://your_server_ip/api/`  
**WebSocket Chat:** `ws://your_server_ip/ws/chat/<conversation_id>/?token=<jwt_token>`  
**WebSocket Notifications:** `ws://your_server_ip/ws/notifications/<user_id>/?token=<jwt_token>`

