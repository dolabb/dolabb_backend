# VPS Web Server Setup Guide

## Problem

Getting `ERR_CONNECTION_TIMED_OUT` when accessing `http://175.161.178.68/media/...`

This means:
- ✅ SFTP is working (files are uploading)
- ❌ Web server (Apache/Nginx) is not running or not configured
- ❌ Firewall might be blocking ports 80/443

## Solution: Set Up Web Server on GoDaddy VPS

### Step 1: Check if Web Server is Installed

SSH into your VPS:
```bash
ssh dolabbadmin@175.161.178.68.host.secureserver.net
```

Check if Apache is installed:
```bash
apache2 -v
# or
httpd -v
```

Check if Nginx is installed:
```bash
nginx -v
```

### Step 2: Install Apache (if not installed)

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install apache2
sudo systemctl start apache2
sudo systemctl enable apache2
```

**For CentOS/RHEL:**
```bash
sudo yum install httpd
sudo systemctl start httpd
sudo systemctl enable httpd
```

### Step 3: Configure Apache for GoDaddy VPS

**Find your Apache config file:**
```bash
# Ubuntu/Debian
sudo nano /etc/apache2/sites-available/000-default.conf

# CentOS/RHEL
sudo nano /etc/httpd/conf/httpd.conf
```

**Update DocumentRoot to point to public_html:**
```apache
<VirtualHost *:80>
    ServerName www.dolabb.com
    ServerAlias dolabb.com
    DocumentRoot /home/dolabbadmin/public_html
    
    <Directory /home/dolabbadmin/public_html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # Serve media files
    Alias /media /home/dolabbadmin/public_html/media
    <Directory /home/dolabbadmin/public_html/media>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

**Enable site and restart Apache:**
```bash
# Ubuntu/Debian
sudo a2ensite 000-default.conf
sudo systemctl restart apache2

# CentOS/RHEL
sudo systemctl restart httpd
```

### Step 4: Configure Firewall

**Check firewall status:**
```bash
sudo ufw status
# or
sudo firewall-cmd --list-all
```

**Open HTTP and HTTPS ports:**
```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Step 5: Test Web Server

1. **Test locally on VPS:**
```bash
curl http://localhost/media/uploads/profiles/
```

2. **Test from your computer:**
```
http://175.161.178.68/media/uploads/profiles/
```

3. **Check Apache status:**
```bash
sudo systemctl status apache2
# or
sudo systemctl status httpd
```

### Step 6: Verify File Access

After setting up web server, test accessing a file:
```
http://175.161.178.68/media/uploads/profiles/ad000d3e-35ac-43f0-b6d9-b1ec62fad5cd.JPG
```

## Alternative: Use cPanel/GoDaddy Control Panel

If you have cPanel or GoDaddy hosting control panel:

1. **Login to cPanel**
2. **Go to File Manager**
3. **Check if public_html is your document root**
4. **Files in public_html/media/ should be accessible at domain.com/media/**

## Quick Check Commands

Run these on your VPS to diagnose:

```bash
# Check if Apache is running
sudo systemctl status apache2
# or
sudo systemctl status httpd

# Check if ports are listening
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check firewall
sudo ufw status
# or
sudo firewall-cmd --list-all

# Test web server
curl http://localhost
```

## Common Issues

### Issue 1: Apache not running
**Solution:** `sudo systemctl start apache2` or `sudo systemctl start httpd`

### Issue 2: Port 80 blocked
**Solution:** Open firewall: `sudo ufw allow 80/tcp`

### Issue 3: Wrong document root
**Solution:** Update Apache config to point to `/home/dolabbadmin/public_html`

### Issue 4: Permission denied
**Solution:** `sudo chmod -R 755 /home/dolabbadmin/public_html`

## After Setup

Once web server is working:
1. Test: `http://175.161.178.68/media/uploads/profiles/` should list files
2. Test: `http://175.161.178.68/media/uploads/profiles/ad000d3e-35ac-43f0-b6d9-b1ec62fad5cd.JPG` should show image
3. Configure DNS to point `www.dolabb.com` to `175.161.178.68`
4. Update `VPS_BASE_URL` to use domain: `https://www.dolabb.com/media`

