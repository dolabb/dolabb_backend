# VPS Storage - Quick Start Guide

## Quick Setup (5 Minutes)

### 1. Install Package
Already added to `requirements.txt`: `paramiko>=2.12.0`

### 2. Set Environment Variables on Render

Go to Render Dashboard → Your Service → Environment → Add:

```
VPS_ENABLED=true
VPS_HOST=your-vps-ip-or-domain.com
VPS_PORT=22
VPS_USERNAME=your-ssh-username
VPS_PASSWORD=your-ssh-password
VPS_BASE_PATH=/var/www/media
VPS_BASE_URL=https://your-vps-domain.com/media
```

### 3. Set Up VPS (One-time)

SSH into your GoDaddy VPS and run:

```bash
# Create directories
sudo mkdir -p /var/www/media/uploads/{profiles,products,chat}
sudo chown -R www-data:www-data /var/www/media
sudo chmod -R 755 /var/www/media
```

### 4. Configure Nginx (if using)

Add to your Nginx config:

```nginx
location /media/ {
    alias /var/www/media/;
    expires 30d;
}
```

### 5. Deploy

Push your code to GitHub and Render will automatically deploy.

## That's It! 🎉

Your images will now be stored on your GoDaddy VPS instead of Render's ephemeral storage.

## Testing

After deployment, upload an image and check:
1. Image appears correctly
2. URL points to your VPS domain
3. Image persists after Render restarts

## Need Help?

See [VPS_STORAGE_SETUP.md](./VPS_STORAGE_SETUP.md) for detailed setup instructions.

