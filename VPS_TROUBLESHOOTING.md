# VPS Storage Troubleshooting Guide

## Issue: Still Getting Render URLs Instead of VPS URLs

If you're still getting `http://dolabb-backend-2vsj.onrender.com/media/...` instead of `https://www.dolabb.com/media/...`, follow these steps:

## Step 1: Check VPS Configuration

Use the diagnostic endpoint to check your VPS configuration:

**Endpoint:** `GET {{base_url}}/api/auth/check-vps-config/`

**Expected Response (if configured correctly):**
```json
{
    "success": true,
    "vps_config": {
        "vps_enabled": true,
        "vps_host": "your-vps-ip-or-domain",
        "vps_port": 22,
        "vps_username": "your-username",
        "vps_base_path": "/var/www/media",
        "vps_base_url": "https://www.dolabb.com/media",
        "has_password": true,
        "has_key": false,
        "status": "configured",
        "missing_fields": []
    }
}
```

**If not configured:**
```json
{
    "success": true,
    "vps_config": {
        "vps_enabled": false,
        "vps_host": "",
        "vps_base_url": "",
        "status": "not_configured",
        "missing_fields": ["vps_host", "vps_username", "vps_base_url"]
    }
}
```

## Step 2: Check Upload Response

After uploading an image, check the response for `storage_type`:

**If using VPS:**
```json
{
    "success": true,
    "message": "Image uploaded successfully",
    "image_url": "https://www.dolabb.com/media/uploads/profiles/...",
    "filename": "...",
    "file_id": "...",
    "storage_type": "vps"
}
```

**If using local storage (fallback):**
```json
{
    "success": true,
    "message": "Image uploaded successfully",
    "image_url": "http://dolabb-backend-2vsj.onrender.com/media/uploads/profiles/...",
    "filename": "...",
    "file_id": "...",
    "storage_type": "local",
    "debug": {
        "vps_enabled": true,
        "vps_host": "...",
        "vps_base_url": "...",
        "reason": "VPS upload failed or not configured properly"
    }
}
```

## Step 3: Verify Environment Variables on Render

1. Go to Render Dashboard → Your Service → Environment
2. Verify these are set:
   - `VPS_ENABLED=true` (must be lowercase 'true')
   - `VPS_HOST=your-vps-ip-or-domain`
   - `VPS_USERNAME=your-ssh-username`
   - `VPS_PASSWORD=your-ssh-password` (or use `VPS_KEY_PATH`)
   - `VPS_BASE_URL=https://www.dolabb.com/media` (no trailing slash)
   - `VPS_BASE_PATH=/var/www/media`

## Step 4: Check Render Logs

After uploading an image, check Render logs for:

**Success:**
```
Image successfully uploaded to VPS: https://www.dolabb.com/media/uploads/profiles/...
```

**Failure:**
```
VPS upload failed, using local storage: [error message]
VPS upload error: [error details], falling back to local storage
```

**Configuration:**
```
VPS Configuration - Enabled: True, Host: ..., Base URL: https://www.dolabb.com/media
```

## Common Issues and Solutions

### Issue 1: VPS_ENABLED is False

**Symptom:** `storage_type: "local"` and `vps_enabled: false` in check-vps-config

**Solution:**
- Set `VPS_ENABLED=true` in Render environment variables
- Make sure it's lowercase 'true', not 'True' or 'TRUE'
- Redeploy your application

### Issue 2: Missing Environment Variables

**Symptom:** `missing_fields` array is not empty in check-vps-config

**Solution:**
- Set all required environment variables:
  - `VPS_HOST`
  - `VPS_USERNAME`
  - `VPS_BASE_URL`
- Redeploy

### Issue 3: VPS Upload Failing

**Symptom:** `storage_type: "local"` but `vps_enabled: true` and `debug.reason` in response

**Possible Causes:**
1. **SSH Connection Failed**
   - Check VPS_HOST is correct
   - Verify VPS is accessible from Render
   - Check firewall allows port 22

2. **Authentication Failed**
   - Verify VPS_USERNAME is correct
   - Check VPS_PASSWORD is correct
   - Or verify VPS_KEY_PATH points to valid SSH key

3. **Directory Doesn't Exist**
   - SSH into VPS: `ssh username@vps-host`
   - Create directory: `sudo mkdir -p /var/www/media/uploads/profiles`
   - Set permissions: `sudo chown -R www-data:www-data /var/www/media`
   - Set permissions: `sudo chmod -R 755 /var/www/media`

4. **Permission Denied**
   - Verify SSH user has write access to `/var/www/media`
   - Check file ownership and permissions

### Issue 4: Wrong URL Format

**Symptom:** URL uses Render domain even though VPS upload succeeded

**Solution:**
- Verify `VPS_BASE_URL=https://www.dolabb.com/media` (no trailing slash)
- Check Nginx is configured to serve `/media/` from `/var/www/media/`

## Testing VPS Connection Manually

SSH into your VPS and test:

```bash
# Test SSH connection
ssh username@vps-host

# Check directory exists
ls -la /var/www/media/uploads/profiles

# Test write permissions
touch /var/www/media/uploads/profiles/test.txt
rm /var/www/media/uploads/profiles/test.txt
```

## Quick Checklist

- [ ] `VPS_ENABLED=true` set in Render (lowercase)
- [ ] `VPS_HOST` set to correct IP/domain
- [ ] `VPS_USERNAME` set correctly
- [ ] `VPS_PASSWORD` or `VPS_KEY_PATH` set correctly
- [ ] `VPS_BASE_URL=https://www.dolabb.com/media` (no trailing slash)
- [ ] VPS directory `/var/www/media/uploads/profiles` exists
- [ ] VPS directory is writable by SSH user
- [ ] Nginx configured to serve `/media/` from `/var/www/media/`
- [ ] Application redeployed after setting environment variables
- [ ] Check diagnostic endpoint shows `status: "configured"`

## Next Steps

1. Call `GET /api/auth/check-vps-config/` to see current configuration
2. Upload an image and check `storage_type` in response
3. Check Render logs for VPS upload errors
4. Fix any issues found
5. Redeploy if environment variables were changed
6. Test again

