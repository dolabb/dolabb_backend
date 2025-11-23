# GoDaddy VPS Storage Setup Guide

## Overview

This guide explains how to set up your GoDaddy VPS to store images and files for
your Django application running on Render.com.

## Prerequisites

1. GoDaddy VPS with SSH access
2. Domain name pointing to your VPS (optional, but recommended)
3. Web server (Nginx or Apache) installed on VPS
4. Python `paramiko` library installed on Render

## Step 1: Install Required Package

On your Render.com application, add `paramiko` to your requirements:

```bash
pip install paramiko
```

Add to `requirements.txt`:

```
paramiko>=2.12.0
```

## Step 2: Set Up VPS Directory Structure

SSH into your GoDaddy VPS and create the media directory:

```bash
# Create media directory
sudo mkdir -p /var/www/media/uploads/profiles
sudo mkdir -p /var/www/media/uploads/products
sudo mkdir -p /var/www/media/chat

# Set permissions (adjust user/group as needed)
sudo chown -R www-data:www-data /var/www/media
sudo chmod -R 755 /var/www/media
```

## Step 3: Set Up Web Server (Nginx Example)

Configure Nginx to serve media files:

```nginx
server {
    listen 80;
    server_name your-vps-domain.com;  # Replace with your domain

    # Media files
    location /media/ {
        alias /var/www/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Optional: Add HTTPS
    # listen 443 ssl;
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;
}
```

## Step 4: Configure Django Settings

Add these settings to your `settings.py` or environment variables:

```python
# VPS Storage Configuration
VPS_ENABLED = os.getenv('VPS_ENABLED', 'False').lower() == 'true'
VPS_HOST = os.getenv('VPS_HOST', '')  # e.g., '123.456.789.0' or 'vps.yourdomain.com'
VPS_PORT = int(os.getenv('VPS_PORT', '22'))
VPS_USERNAME = os.getenv('VPS_USERNAME', '')
VPS_PASSWORD = os.getenv('VPS_PASSWORD', '')  # Or use SSH key
VPS_KEY_PATH = os.getenv('VPS_KEY_PATH', '')  # Path to SSH private key (optional)
VPS_BASE_PATH = os.getenv('VPS_BASE_PATH', '/var/www/media')
VPS_BASE_URL = os.getenv('VPS_BASE_URL', '')  # e.g., 'https://vps.yourdomain.com/media' or 'http://123.456.789.0/media'
```

## Step 5: Set Environment Variables on Render

In your Render.com dashboard:

1. Go to your service → Environment
2. Add these environment variables:

```
VPS_ENABLED=true
VPS_HOST=your-vps-ip-or-domain
VPS_PORT=22
VPS_USERNAME=your-ssh-username
VPS_PASSWORD=your-ssh-password
VPS_BASE_PATH=/var/www/media
VPS_BASE_URL=https://your-vps-domain.com/media
```

**Security Note**: For better security, use SSH key authentication instead of
password:

1. Generate SSH key pair on Render (or locally)
2. Add public key to VPS: `~/.ssh/authorized_keys`
3. Store private key securely (use Render secrets or environment variable)
4. Set `VPS_KEY_PATH` to the path of your private key

## Step 6: SSH Key Setup (Recommended)

### Generate SSH Key

```bash
# On your local machine or Render
ssh-keygen -t rsa -b 4096 -f vps_key -N ""
```

### Add Public Key to VPS

```bash
# Copy public key to VPS
ssh-copy-id -i vps_key.pub username@your-vps-ip

# Or manually:
cat vps_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Store Private Key on Render

1. Copy private key content
2. In Render dashboard → Environment → Secrets
3. Add as `VPS_PRIVATE_KEY` (base64 encoded or as multiline secret)
4. Or upload key file and set `VPS_KEY_PATH`

## Step 7: Test the Setup

Test the connection from your Render application:

```python
# Test script (run once)
from storage.vps_helper import upload_file_to_vps

test_content = b"test file content"
success, result = upload_file_to_vps(test_content, 'uploads/test', 'test.txt')
print(f"Success: {success}, Result: {result}")
```

## Step 8: Firewall Configuration

Ensure your VPS firewall allows SSH (port 22):

```bash
# UFW example
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Directory Structure on VPS

```
/var/www/media/
├── uploads/
│   ├── profiles/
│   │   └── [uuid].jpg
│   └── products/
│       └── [uuid].jpg
└── chat/
    └── [files]
```

## URL Structure

Files will be accessible at:

- Profiles: `https://your-vps-domain.com/media/uploads/profiles/[filename]`
- Products: `https://your-vps-domain.com/media/uploads/products/[filename]`
- Chat: `https://your-vps-domain.com/media/chat/[filename]`

## Security Considerations

1. **Use SSH Keys**: Prefer SSH key authentication over passwords
2. **Restrict SSH Access**: Use firewall rules to limit SSH access to Render IPs
3. **HTTPS**: Use HTTPS for serving files (Let's Encrypt free SSL)
4. **File Permissions**: Set appropriate file permissions (755 for directories,
   644 for files)
5. **Regular Backups**: Backup your VPS media directory regularly

## Troubleshooting

### Connection Timeout

- Check VPS firewall allows port 22
- Verify VPS_HOST and VPS_PORT are correct
- Check if VPS is accessible from Render

### Permission Denied

- Verify SSH user has write permissions to `/var/www/media`
- Check file ownership: `sudo chown -R www-data:www-data /var/www/media`

### Files Not Accessible via URL

- Verify Nginx/Apache is configured correctly
- Check file permissions
- Ensure VPS_BASE_URL matches your actual domain/IP

### Authentication Failed

- Verify username and password are correct
- If using SSH key, check key permissions: `chmod 600 vps_key`
- Test SSH connection manually: `ssh -i vps_key username@vps-host`

## Fallback Behavior

If VPS upload fails, the system will automatically fall back to local storage on
Render. This ensures your application continues to work even if VPS is
temporarily unavailable.

## Monitoring

Monitor your application logs for:

- VPS connection errors
- Upload failures
- Fallback to local storage warnings

## Cost Considerations

- GoDaddy VPS: Your existing VPS cost
- Storage: Limited by VPS disk space
- Bandwidth: Check your VPS bandwidth limits
- Render: No additional cost (uses existing service)

## Next Steps

1. Set up environment variables on Render
2. Test file upload
3. Monitor logs for any issues
4. Set up automated backups of VPS media directory
5. Consider setting up CDN for better performance (optional)

## Support

If you encounter issues:

1. Check Render application logs
2. Check VPS system logs: `tail -f /var/log/auth.log`
3. Test SSH connection manually
4. Verify all environment variables are set correctly
