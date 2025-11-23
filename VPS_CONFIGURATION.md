# VPS Configuration for dolabb.com

## Required Environment Variables on Render

Set these in your Render.com dashboard → Your Service → Environment:

```
VPS_ENABLED=true
VPS_HOST=your-vps-ip-or-domain
VPS_PORT=22
VPS_USERNAME=your-ssh-username
VPS_PASSWORD=your-ssh-password
VPS_BASE_PATH=/home/dolabbadmin/public_html/media
VPS_BASE_URL=https://www.dolabb.com/media
```

**Important Notes:**
- `VPS_BASE_URL` should be `https://www.dolabb.com/media` (no trailing slash)
- `VPS_ENABLED` must be exactly `true` (lowercase)
- Make sure your VPS has the directories created: `public_html/media/uploads/profiles` (with 755 permissions)

## Expected Response After Configuration

Once configured, the upload image API will return:

```json
{
    "success": true,
    "message": "Image uploaded successfully",
    "image_url": "https://www.dolabb.com/media/uploads/profiles/57d20dd2-2c4e-447a-94b0-57a8bfe1c4bd.JPG",
    "filename": "57d20dd2-2c4e-447a-94b0-57a8bfe1c4bd.JPG",
    "file_id": "692254273601cc3e348681a1"
}
```

## Troubleshooting

If you're still getting Render URLs:

1. **Check VPS_ENABLED**: Must be set to `true` (not `True` or `TRUE`)
2. **Check VPS_BASE_URL**: Should be `https://www.dolabb.com/media` (no trailing slash)
3. **Check VPS credentials**: Verify SSH connection works
4. **Check logs**: Look for "VPS upload failed" warnings in Render logs
5. **Verify VPS directory exists**: `public_html/media/uploads/profiles` must exist and be writable (755 permissions)

## Testing VPS Connection

You can test if VPS is working by checking the Render logs after uploading an image. You should see:
- `"Image successfully uploaded to VPS: https://www.dolabb.com/media/..."` if successful
- `"VPS upload failed, using local storage: ..."` if there's an issue

## Web Server Configuration on VPS

Make sure your web server (Apache/Nginx) is configured to serve files from `public_html/media`:

**For Apache (typical GoDaddy setup):**
- Files in `public_html/media/` are automatically served at `https://www.dolabb.com/media/`
- No additional configuration needed if `public_html` is your document root

**For Nginx:**
```nginx
location /media/ {
    alias /home/dolabbadmin/public_html/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

