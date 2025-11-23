# VPS Host Configuration Fix

## Problem

Getting error: `[Errno -2] Name or service not known` when trying to connect to VPS.

The hostname `68.178.161.175.host.secureserver.net` cannot be resolved.

## Solution: Use IP Address Directly

For GoDaddy VPS, you can use the IP address directly instead of the hostname.

### Update Environment Variable in Render:

**Change:**
```
VPS_HOST=68.178.161.175.host.secureserver.net
```

**To:**
```
VPS_HOST=175.161.178.68
```

**Or if the IP is different, use the correct IP address.**

## How to Find Your VPS IP Address

1. **From GoDaddy Control Panel:**
   - Login to GoDaddy
   - Go to your VPS management
   - Check the IP address shown

2. **From SSH (if you can connect):**
   ```bash
   hostname -I
   # or
   ip addr show
   ```

3. **From your domain:**
   ```bash
   nslookup www.dolabb.com
   # or
   ping www.dolabb.com
   ```

## Complete Environment Variables

Make sure these are set correctly in Render:

```
VPS_ENABLED=true
VPS_HOST=175.161.178.68
VPS_PORT=22
VPS_USERNAME=dolabbadmin
VPS_PASSWORD=your-ssh-password
VPS_BASE_PATH=/home/dolabbadmin/public_html/media
VPS_BASE_URL=https://www.dolabb.com/media
```

**Important:** Use the IP address directly (e.g., `175.161.178.68`) instead of the hostname if the hostname doesn't resolve.

## After Updating

1. Save the environment variable in Render
2. Wait for deployment to complete
3. Test the upload-image API again
4. You should get `storage_type: "vps"` in the response

