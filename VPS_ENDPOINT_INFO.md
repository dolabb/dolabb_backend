# VPS Configuration Check Endpoint

## Endpoint Information

**URL:** `{{base_url}}/api/auth/check-vps-config/`

**Method:** `GET` or `POST` (both work)

**Headers:** No special headers required (public endpoint)

**Authentication:** Not required (public endpoint for debugging)

## Usage in Postman

1. **Method:** GET or POST
2. **URL:** `https://dolabb-backend-2vsj.onrender.com/api/auth/check-vps-config/`
3. **Headers:** None required (or just `Content-Type: application/json`)
4. **Body:** None required for GET

## Alternative: Check VPS Info in Upload Response

If the endpoint is not available yet (code not deployed), you can check VPS configuration in the upload image response:

**Endpoint:** `POST {{base_url}}/api/auth/upload-image/`

The response will now include `vps_info`:

```json
{
    "success": true,
    "message": "Image uploaded successfully",
    "image_url": "...",
    "filename": "...",
    "file_id": "...",
    "storage_type": "local",
    "vps_info": {
        "vps_enabled": false,
        "vps_configured": false,
        "vps_base_url": "Not set"
    }
}
```

## Expected Response from check-vps-config

**If VPS is configured:**
```json
{
    "success": true,
    "message": "VPS configuration check completed",
    "vps_config": {
        "vps_enabled": true,
        "vps_host": "your-vps-ip",
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

**If VPS is not configured:**
```json
{
    "success": true,
    "message": "VPS configuration check completed",
    "vps_config": {
        "vps_enabled": false,
        "vps_host": "",
        "vps_port": 22,
        "vps_username": "",
        "vps_base_path": "/var/www/media",
        "vps_base_url": "",
        "has_password": false,
        "has_key": false,
        "status": "not_configured",
        "missing_fields": ["vps_host", "vps_username", "vps_base_url"]
    }
}
```

## Troubleshooting 404 Error

If you get a 404 "Not Found" error:

1. **Code not deployed yet**: The endpoint was just added. You need to:
   - Push code to GitHub
   - Wait for Render to auto-deploy
   - Or manually trigger deployment

2. **Try without trailing slash**: 
   - `{{base_url}}/api/auth/check-vps-config` (no trailing slash)

3. **Check base URL**: Make sure `{{base_url}}` is `https://dolabb-backend-2vsj.onrender.com`

4. **Use upload endpoint instead**: Check `vps_info` in the upload image response (available immediately)

## Quick Check Without Endpoint

You can also check VPS configuration by:

1. Upload an image via `POST /api/auth/upload-image/`
2. Check the `vps_info` field in the response
3. If `vps_enabled: false`, VPS is not enabled
4. If `vps_base_url: "Not set"`, environment variables are not configured

