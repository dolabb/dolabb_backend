# Fix VPS Permission Error

## Current Error

```
Failed to create directory /var/www/media: [Errno 13] Permission denied
```

## Solution Options

### Option 1: Create Directory with Proper Permissions (Recommended)

SSH into your VPS and run:

```bash
# SSH into VPS
ssh dolabbadmin@175.161.178.68.host.secureserver.net

# Create directory structure
sudo mkdir -p /var/www/media/uploads/profiles
sudo mkdir -p /var/www/media/uploads/products
sudo mkdir -p /var/www/media/chat

# Set ownership to your SSH user
sudo chown -R dolabbadmin:dolabbadmin /var/www/media

# Set permissions
sudo chmod -R 755 /var/www/media
```

### Option 2: Use Home Directory (Easier)

If you can't modify `/var/www/media`, use a directory in your home folder:

1. **On VPS:**

```bash
# Create directory in home folder
mkdir -p ~/media/uploads/profiles
mkdir -p ~/media/uploads/products
mkdir -p ~/media/chat
chmod -R 755 ~/media
```

2. **Update Render Environment Variables:**

```
VPS_BASE_PATH=/home/dolabbadmin/media
```

3. **Update Nginx Configuration:**

```nginx
location /media/ {
    alias /home/dolabbadmin/media/;
    expires 30d;
}
```

### Option 3: Use /tmp or /opt (Alternative)

```bash
# Create in /opt
sudo mkdir -p /opt/dolabb-media/uploads/profiles
sudo chown -R dolabbadmin:dolabbadmin /opt/dolabb-media
sudo chmod -R 755 /opt/dolabb-media
```

Then update `VPS_BASE_PATH=/opt/dolabb-media` in Render.

## Quick Fix (Recommended)

Run these commands on your VPS:

```bash
ssh dolabbadmin@175.161.178.68.host.secureserver.net

# Create and set permissions
sudo mkdir -p /var/www/media/uploads/{profiles,products,chat}
sudo chown -R dolabbadmin:dolabbadmin /var/www/media
sudo chmod -R 755 /var/www/media

# Verify
ls -la /var/www/media
touch /var/www/media/uploads/profiles/test.txt
rm /var/www/media/uploads/profiles/test.txt
```

If the last two commands work, permissions are correct!

## After Fixing Permissions

1. Test upload again - should work now
2. Image URL should be: `https://www.dolabb.com/media/uploads/profiles/...`
3. Check that files appear in `/var/www/media/uploads/profiles/` on VPS
