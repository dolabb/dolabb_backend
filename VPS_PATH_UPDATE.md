# Update VPS_BASE_PATH for GoDaddy VPS

## Issue

Your folders are in `public_html/media/uploads/` but the code is trying to use `/var/www/media`.

## Solution

Update the `VPS_BASE_PATH` environment variable on Render to match your actual folder structure.

## Steps

1. **Go to Render Dashboard** → Your Service → Environment

2. **Update or Add this environment variable:**
   ```
   VPS_BASE_PATH=/home/dolabbadmin/public_html/media
   ```
   
   **OR** if your `public_html` is in a different location, use the full path:
   ```
   VPS_BASE_PATH=/var/www/html/public_html/media
   ```
   
   To find the exact path, SSH into your VPS and run:
   ```bash
   pwd
   # or
   echo $HOME
   # Then check where public_html is
   ls -la ~/public_html
   ```

3. **Redeploy** your application on Render

4. **Test** by uploading an image - it should now work!

## Common GoDaddy VPS Paths

- `/home/dolabbadmin/public_html/media` (most common)
- `/home/username/public_html/media` (if different username)
- `/var/www/html/public_html/media` (some configurations)

## Verify Path

To verify the correct path, SSH into your VPS:
```bash
ssh dolabbadmin@175.161.178.68.host.secureserver.net
pwd
cd public_html
pwd
# This will show the full path, e.g., /home/dolabbadmin/public_html
```

Then use that full path + `/media` for `VPS_BASE_PATH`.

