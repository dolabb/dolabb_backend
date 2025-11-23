# VPS Upload Error Solutions

## Common Error Messages and Solutions

Based on the error message in the `debug.error` field, here are the solutions:

### 1. "VPS Authentication failed"

**Error:** `VPS Authentication failed: ...`

**Solutions:**
- Verify `VPS_USERNAME` is correct
- Verify `VPS_PASSWORD` is correct (no extra spaces)
- If using SSH key, verify `VPS_KEY_PATH` points to valid key file
- Test SSH connection manually: `ssh username@vps-host`

### 2. "VPS SSH connection error"

**Error:** `VPS SSH connection error: ...`

**Solutions:**
- Verify `VPS_HOST` is correct (IP or domain)
- Check if VPS firewall allows port 22 from Render
- Verify `VPS_PORT` is correct (usually 22)
- Test network connectivity: `ping vps-host`
- Check if VPS is accessible from Render's network

### 3. "Failed to create directory"

**Error:** `Failed to create directory ... Check permissions on VPS`

**Solutions:**
- SSH into VPS: `ssh username@vps-host`
- Create directory manually: `sudo mkdir -p /var/www/media/uploads/profiles`
- Set ownership: `sudo chown -R username:username /var/www/media`
- Set permissions: `sudo chmod -R 755 /var/www/media`
- Or use a directory the user owns: `/home/username/media/uploads/profiles`

### 4. "Failed to write file to VPS"

**Error:** `Failed to write file to VPS: ... Check directory permissions`

**Solutions:**
- Verify directory exists: `ls -la /var/www/media/uploads/profiles`
- Check write permissions: `touch /var/www/media/uploads/profiles/test.txt`
- Fix permissions: `sudo chmod -R 755 /var/www/media`
- Fix ownership: `sudo chown -R username:username /var/www/media`

### 5. "VPS connection failed"

**Error:** `VPS connection failed: ...`

**Solutions:**
- Check VPS is running and accessible
- Verify VPS_HOST format (IP address or domain name)
- Check firewall rules allow SSH (port 22)
- Test SSH from local machine first
- Check if VPS has IP restrictions

## Quick Diagnostic Steps

1. **Check the error message** in `debug.error` field
2. **SSH into VPS manually** to verify credentials work
3. **Check directory exists and permissions**
4. **Test file write** manually on VPS
5. **Check Render logs** for detailed error traceback

## Your Current Configuration

Based on your response:
- ✅ VPS Enabled: `true`
- ✅ VPS Configured: `true`
- ✅ VPS Host: `175.161.178.68.host.secureserver.net`
- ✅ VPS Base URL: `https://www.dolabb.com/media`
- ❌ Upload Failing: Check `debug.error` for specific error

## Next Steps

1. Upload an image again and check the `debug.error` field
2. The error message will tell you exactly what's wrong
3. Follow the solution for that specific error
4. Test again

