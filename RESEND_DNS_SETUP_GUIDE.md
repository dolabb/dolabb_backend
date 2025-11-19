# Resend DNS Setup Guide for dolabb.com

## Overview
This guide will help you configure DNS records for your domain `dolabb.com` in Resend to enable sending emails from `no-reply@dolabb.com`.

## ⚠️ IMPORTANT: DNS Setup is REQUIRED

**Yes, DNS setup is REQUIRED** to send emails from your custom domain. Without proper DNS configuration:
- Resend cannot verify your domain ownership
- Emails will not be delivered
- You'll get authentication errors

## Step-by-Step DNS Configuration

### Step 1: Add Domain in Resend Dashboard

1. Log in to your Resend account: https://resend.com
2. Go to **Domains** section in the dashboard
3. Click **Add Domain**
4. Enter your domain: `dolabb.com`
5. Click **Add Domain**

### Step 2: Get DNS Records from Resend

After adding the domain, Resend will show you the DNS records you need to add. Typically, you'll need:

1. **SPF Record** (TXT record)
   - Name: `@` or `dolabb.com`
   - Value: `v=spf1 include:resend.com ~all`
   - Purpose: Authorizes Resend to send emails on your behalf

2. **DKIM Record** (TXT record)
   - Name: `resend._domainkey` or similar
   - Value: A long string provided by Resend (unique to your account)
   - Purpose: Email authentication to prevent spoofing

3. **DMARC Record** (TXT record) - Optional but recommended
   - Name: `_dmarc`
   - Value: `v=DMARC1; p=none; rua=mailto:dmarc@dolabb.com`
   - Purpose: Email authentication policy

### Step 3: Add DNS Records to Your Domain Provider

You need to add these DNS records where you manage your domain (e.g., GoDaddy, Namecheap, Cloudflare, etc.):

#### For Most Domain Providers:

1. Log in to your domain registrar (where you bought dolabb.com)
2. Navigate to **DNS Management** or **DNS Settings**
3. Add the TXT records provided by Resend:

**Example DNS Records:**

```
Type: TXT
Name: @
Value: v=spf1 include:resend.com ~all
TTL: 3600 (or default)

Type: TXT
Name: resend._domainkey
Value: [The long DKIM string from Resend]
TTL: 3600 (or default)

Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@dolabb.com
TTL: 3600 (or default)
```

#### For Cloudflare Users:

1. Go to Cloudflare Dashboard → Select `dolabb.com`
2. Click **DNS** → **Records**
3. Click **Add record**
4. Add each TXT record:
   - Type: `TXT`
   - Name: `@` (for root domain) or `resend._domainkey` (for DKIM)
   - Content: The value from Resend
   - TTL: Auto or 3600
5. Click **Save**

### Step 4: Verify Domain in Resend

1. After adding DNS records, go back to Resend dashboard
2. Click on your domain `dolabb.com`
3. Click **Verify Domain** or wait for automatic verification
4. DNS propagation can take **5 minutes to 48 hours** (usually 15-30 minutes)
5. Once verified, you'll see a green checkmark ✅

### Step 5: Verify DNS Records

You can check if DNS records are properly set using:

**Online Tools:**
- https://mxtoolbox.com/spf.aspx (for SPF)
- https://mxtoolbox.com/dkim.aspx (for DKIM)
- https://dnschecker.org (to check DNS propagation)

**Command Line:**
```bash
# Check SPF record
nslookup -type=TXT dolabb.com

# Check DKIM record
nslookup -type=TXT resend._domainkey.dolabb.com

# Check DMARC record
nslookup -type=TXT _dmarc.dolabb.com
```

## Step 6: Configure Backend Environment Variables

Once your domain is verified in Resend:

1. **Update Render Environment Variables:**
   - Go to Render Dashboard → Your Web Service → Environment
   - Update `RESEND_API_KEY` to: `re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ`
   - Update `RESEND_FROM_EMAIL` to: `no-reply@dolabb.com`
   - Save and redeploy your service

2. **For Local Development (.env file):**
   ```
   RESEND_API_KEY=re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ
   RESEND_FROM_EMAIL=no-reply@dolabb.com
   ```

## Testing Email Sending

After DNS is verified and environment variables are set:

1. Test OTP email by triggering a signup/login
2. Check Resend dashboard → **Logs** to see email delivery status
3. Check spam folder if email doesn't arrive

## Troubleshooting

### Domain Not Verifying?

1. **Wait longer**: DNS can take up to 48 hours to propagate
2. **Check DNS records**: Use DNS checker tools to verify records are live
3. **Check for typos**: Ensure DNS record values match exactly what Resend provided
4. **Check TTL**: Lower TTL (300-600) can help with faster updates

### Emails Not Sending?

1. **Verify domain status**: Check Resend dashboard - domain must show as "Verified"
2. **Check API key**: Ensure `RESEND_API_KEY` is correct in environment variables
3. **Check FROM email**: Must match verified domain (e.g., `no-reply@dolabb.com`)
4. **Check Resend logs**: Dashboard → Logs shows delivery errors

### Common DNS Errors:

- **"SPF record not found"**: Add the SPF TXT record
- **"DKIM verification failed"**: Check DKIM record name and value match exactly
- **"Domain not verified"**: Wait for DNS propagation and click Verify again

## Important Notes

1. **DNS Propagation**: Changes can take 5 minutes to 48 hours to propagate globally
2. **Case Sensitivity**: DNS record names are case-insensitive, but values must match exactly
3. **Multiple Records**: You can have multiple TXT records for the same name
4. **TTL**: Time To Live - how long DNS servers cache the record (lower = faster updates)

## Support

- Resend Documentation: https://resend.com/docs
- Resend Support: support@resend.com
- Resend Status: https://status.resend.com

## Quick Checklist

- [ ] Added domain `dolabb.com` in Resend dashboard
- [ ] Added SPF TXT record to domain DNS
- [ ] Added DKIM TXT record to domain DNS
- [ ] Added DMARC TXT record (optional but recommended)
- [ ] Verified domain in Resend (green checkmark)
- [ ] Updated `RESEND_API_KEY` in Render environment variables
- [ ] Updated `RESEND_FROM_EMAIL` to `no-reply@dolabb.com` in Render
- [ ] Redeployed backend service on Render
- [ ] Tested OTP email sending

---

**Last Updated**: 2025-01-27
**Domain**: dolabb.com
**Email Address**: no-reply@dolabb.com
**Resend API Key**: re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ

