# VPS DNS/Domain Issue - Solutions

## Problem

Getting `DNS_PROBE_FINISHED_NXDOMAIN` when accessing `https://www.dolabb.com/media/...`
OR
Getting `ERR_CONNECTION_TIMED_OUT` when accessing `http://175.161.178.68/media/...`

This means:
- ✅ Files are uploading to VPS successfully (SFTP works)
- ❌ Web server (Apache/Nginx) is not running or not configured
- ❌ Firewall might be blocking HTTP ports (80/443)
- ❌ Domain DNS not configured (if using domain)

## Primary Issue: Web Server Not Running

**The connection timeout means your VPS doesn't have a web server running or configured.**

See **[VPS_WEBSERVER_SETUP.md](./VPS_WEBSERVER_SETUP.md)** for complete web server setup instructions.

## Solution Options

### Option 1: Use VPS IP Address (Quick Fix)

If your domain is not configured yet, you can use the VPS IP address directly:

**Update on Render:**
```
VPS_BASE_URL=http://175.161.178.68/media
```

**Note:** Use `http://` instead of `https://` unless you have SSL configured on the IP.

**Limitations:**
- URLs will show IP address instead of domain
- Less professional
- May not work if VPS requires domain-based virtual host

### Option 2: Configure Domain DNS (Recommended)

1. **Point Domain to VPS IP:**
   - Go to your domain registrar (GoDaddy, etc.)
   - Add/Update DNS A record:
     - Type: `A`
     - Host: `@` or `www`
     - Value: `175.161.178.68`
     - TTL: `3600` or default

2. **Wait for DNS Propagation:**
   - Can take 24-48 hours
   - Check with: `nslookup www.dolabb.com` or `ping www.dolabb.com`

3. **Configure Virtual Host on VPS:**
   - Make sure Apache/Nginx is configured to serve `www.dolabb.com`
   - Document root should point to `public_html`

### Option 3: Use Subdomain

If main domain is not ready, use a subdomain:
```
VPS_BASE_URL=https://media.dolabb.com/media
```

Then configure DNS:
- Type: `A`
- Host: `media`
- Value: `175.161.178.68`

### Option 4: Test with Direct IP Access

Test if files are accessible via IP:
```
http://175.161.178.68/media/uploads/profiles/ad000d3e-35ac-43f0-b6d9-b1ec62fad5cd.JPG
```

If this works, the issue is only DNS/domain configuration.

## Quick Test

1. **Test IP access:**
   ```
   http://175.161.178.68/media/uploads/profiles/ad000d3e-35ac-43f0-b6d9-b1ec62fad5cd.JPG
   ```

2. **Check DNS:**
   ```bash
   nslookup www.dolabb.com
   ping www.dolabb.com
   ```

3. **Check VPS web server config:**
   - Verify Apache/Nginx is running
   - Check if virtual host is configured for `www.dolabb.com`
   - Verify `public_html` is the document root

## Temporary Workaround

While fixing DNS, you can:
1. Use IP address in `VPS_BASE_URL`
2. Or keep using local storage on Render (files will be lost on restart)
3. Or wait for DNS to propagate

## Recommended Action

1. **Immediate:** Test with IP address to verify files are accessible
2. **Short-term:** Configure DNS A record pointing to VPS IP
3. **Long-term:** Set up SSL certificate for HTTPS

