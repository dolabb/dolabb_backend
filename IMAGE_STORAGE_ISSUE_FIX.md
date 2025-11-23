# Image Storage Issue - Analysis and Fix

## Problem

Images uploaded during signup work initially but then become inaccessible, showing "Not Found" errors when accessed via URL.

## Root Cause

The issue is likely due to **ephemeral filesystem** on Render.com (or similar hosting platforms):

1. **Files are saved to local filesystem** (`MEDIA_ROOT/uploads/profiles/`)
2. **Files are lost** when:
   - Server restarts
   - Application redeploys
   - Container is recreated
   - System maintenance occurs

This is common with free-tier hosting services that use ephemeral storage.

## Changes Made

### 1. Improved URL Generation
- Fixed URL construction to use `request.build_absolute_uri()` for consistency
- Added proper path normalization
- Ensured URLs are always correctly formatted

### 2. File Verification
- Added checks to verify files are saved before returning URLs
- Added logging to track file save operations
- Better error handling if file save fails

### 3. Enhanced Error Handling
- Added logging in `serve_media_file` to debug file access issues
- Better error messages for troubleshooting

## Current Status

✅ **Fixed**: URL generation and file verification
⚠️ **Limitation**: Files still stored on ephemeral filesystem

## Recommended Solutions

### Option 1: Use Cloud Storage (Recommended)

For production, use cloud storage services:

#### AWS S3
```python
# Install: pip install django-storages boto3
# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
```

#### Cloudinary
```python
# Install: pip install cloudinary django-cloudinary-storage
# settings.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

#### DigitalOcean Spaces
```python
# Similar to S3 configuration
```

### Option 2: Use Render Disk (Temporary Solution)

If using Render.com, you can add a persistent disk:
- Go to Render Dashboard → Your Service → Settings
- Add a persistent disk
- Mount it to your application
- Update `MEDIA_ROOT` to use the mounted disk

**Note**: This is a paid feature on Render.

### Option 3: Database Storage (Not Recommended)

Store images as base64 in MongoDB (what we're trying to avoid):
- Increases database size significantly
- Slower queries
- Not scalable

## Testing the Fix

1. **Check file exists after save**:
   ```python
   # Logs will show if file was saved successfully
   ```

2. **Verify URL format**:
   - Should be: `https://dolabb-backend-2vsj.onrender.com/media/uploads/profiles/{filename}`
   - Check browser console for 404 errors

3. **Check server logs**:
   - Look for "File not found" warnings
   - Check if directory exists
   - Verify file path matches

## Immediate Actions

1. ✅ Code fixes applied (URL generation, file verification)
2. ⚠️ Monitor logs for file access issues
3. 🔄 Plan migration to cloud storage for production

## Migration Path to Cloud Storage

1. Set up cloud storage account (AWS S3, Cloudinary, etc.)
2. Install required packages
3. Update settings.py with cloud storage configuration
4. Migrate existing files (if any)
5. Test image upload/access
6. Deploy to production

## Notes

- **MongoDB is not the issue** - Images are stored on filesystem, not in database
- **URLs are stored in MongoDB** - Only the URL string is saved, not the file
- **Files must persist on filesystem** - Or use cloud storage

## Support

If images continue to disappear:
1. Check Render.com logs for file system errors
2. Verify MEDIA_ROOT directory exists and is writable
3. Consider upgrading to persistent storage or cloud storage

