# 🚀 Quick Deployment Checklist

> **For Windows users:** See `WINDOWS_DEPLOYMENT_GUIDE.md` for detailed Windows-specific instructions.

## Before You Start

1. **SSH into your GoDaddy VPS**
   - Windows: Use Windows Terminal or PuTTY
   - Mac/Linux: Use Terminal
2. **Make sure you have:**
   - MongoDB connection string
   - All API keys (Resend, Moyasar)
   - Your domain name or server IP

## Quick Steps

### 1. Upload Code to Server

```bash
# Option 1: Using SCP (from your local machine)
scp -r . root@your_server_ip:/var/www/dolabb_backend

# Option 2: Using Git
cd /var/www
git clone your_repo_url dolabb_backend
```

### 2. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx redis-server git
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 3. Set Up Python Environment

```bash
cd /var/www/dolabb_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create .env File

```bash
nano .env
```

Add all your production environment variables (see DEPLOYMENT_GUIDE.md for full list)

### 5. Collect Static Files

```bash
export DJANGO_SETTINGS_MODULE=dolabb_backend.settings_production
python manage.py collectstatic --noinput
```

### 6. Set Up Services

```bash
# Copy systemd service files
sudo cp systemd/dolabb-backend.service /etc/systemd/system/
sudo cp systemd/dolabb-daphne.service /etc/systemd/system/

# Edit paths in service files
sudo nano /etc/systemd/system/dolabb-backend.service
sudo nano /etc/systemd/system/dolabb-daphne.service
# Update: /path/to/your/project → /var/www/dolabb_backend

# Set permissions
sudo chown -R www-data:www-data /var/www/dolabb_backend

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable dolabb-backend dolabb-daphne
sudo systemctl start dolabb-backend dolabb-daphne
```

### 7. Configure Nginx

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/dolabb_backend

# Edit and update:
# - your_domain.com → your actual domain
# - /path/to/your/project → /var/www/dolabb_backend

sudo nano /etc/nginx/sites-available/dolabb_backend

# Enable site
sudo ln -s /etc/nginx/sites-available/dolabb_backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. Test

```bash
# Check services
sudo systemctl status dolabb-backend
sudo systemctl status dolabb-daphne
sudo systemctl status nginx
sudo systemctl status redis-server

# Test API
curl http://your_domain.com/api/products/
```

## WebSocket URLs

- **Chat:** `ws://your_domain.com/ws/chat/<conversation_id>/?token=<jwt_token>`
- **Notifications:** `ws://your_domain.com/ws/notifications/<user_id>/?token=<jwt_token>`

## Important Notes

- Replace all `/path/to/your/project` with `/var/www/dolabb_backend`
- Replace `your_domain.com` with your actual domain or IP
- Make sure Redis is running: `redis-cli ping` (should return PONG)
- Check logs if issues: `sudo journalctl -u dolabb-backend -f`

## Full Guide

See `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.

