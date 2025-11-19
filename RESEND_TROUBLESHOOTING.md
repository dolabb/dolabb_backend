# Resend Email Troubleshooting Guide

## Common Error: "You can only send testing emails to your own email address"

### What This Error Means

This error occurs when:
1. **You're using a test/development API key** - Test keys only allow sending to the account owner's email
2. **Your domain is not verified** - Resend requires domain verification for production emails
3. **The FROM email doesn't match your verified domain** - The FROM address must use your verified domain

### Error Message Example

```
Failed to send OTP email: You can only send testing emails to your own email address (anaspirzada510@gmail.com). 
To send emails to other recipients, please verify a domain at resend.com/domains, 
and change the `from` address to an email using this domain.
```

### Solutions

#### Solution 1: Verify Your Domain in Resend

1. **Go to Resend Dashboard**: https://resend.com/domains
2. **Check Domain Status**: Look for `dolabb.com` - it should show as "Verified" ✅
3. **If Not Verified**:
   - Click on your domain
   - Add the DNS records (SPF, DKIM, DMARC) to your domain provider
   - Wait for verification (5 minutes to 48 hours)
   - See `RESEND_DNS_SETUP_GUIDE.md` for detailed instructions

#### Solution 2: Check Your API Key

1. **Verify API Key Type**:
   - Go to Resend Dashboard → API Keys
   - Ensure you're using a **Production API Key**, not a test key
   - Test keys start with `re_test_` or have restrictions
   - Production keys start with `re_` (like `re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ`)

2. **Update Environment Variables**:
   - In Render Dashboard → Your Web Service → Environment
   - Set `RESEND_API_KEY` to your production API key
   - Ensure it matches the key from your Resend account

#### Solution 3: Verify FROM Email Address

1. **Check Current FROM Email**:
   - In Render Dashboard → Environment Variables
   - Verify `RESEND_FROM_EMAIL` is set to: `no-reply@dolabb.com`
   - NOT `onboarding@resend.dev` or `noreply@yourdomain.com`

2. **Domain Must Match**:
   - The FROM email domain (`dolabb.com`) must be verified in Resend
   - The email address (`no-reply@dolabb.com`) must use your verified domain

#### Solution 4: Check DNS Records

1. **Verify DNS Propagation**:
   - Use https://dnschecker.org to check if DNS records are live
   - Check SPF: `nslookup -type=TXT dolabb.com`
   - Check DKIM: `nslookup -type=TXT resend._domainkey.dolabb.com`

2. **Common DNS Issues**:
   - Records not propagated yet (wait 15-30 minutes)
   - Typos in DNS record values
   - Wrong record type (must be TXT records)
   - TTL too high (lower TTL = faster updates)

### Step-by-Step Verification Checklist

- [ ] Domain `dolabb.com` is added in Resend dashboard
- [ ] Domain shows as "Verified" ✅ in Resend dashboard
- [ ] DNS records (SPF, DKIM, DMARC) are added to domain provider
- [ ] DNS records are propagated (check with DNS checker tools)
- [ ] Using production API key (not test key)
- [ ] `RESEND_API_KEY` environment variable is set correctly in Render
- [ ] `RESEND_FROM_EMAIL` is set to `no-reply@dolabb.com` in Render
- [ ] Backend service has been redeployed after environment variable changes
- [ ] Tested sending email to a different email address (not account owner)

### Testing Your Configuration

1. **Check Environment Variables**:
   ```bash
   # In Render, check that these are set:
   RESEND_API_KEY=re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ
   RESEND_FROM_EMAIL=no-reply@dolabb.com
   ```

2. **Test Email Sending**:
   - Try creating a user with a different email (not anaspirzada510@gmail.com)
   - Check Resend dashboard → Logs for email delivery status
   - Check for any error messages

3. **Verify Domain Status**:
   - Go to Resend Dashboard → Domains
   - Click on `dolabb.com`
   - Ensure status is "Verified" with green checkmark

### Why Users Are Still Saved Despite Email Errors

**Previous Issue (Now Fixed)**:
- Users were saved to MongoDB BEFORE sending the email
- If email failed, user remained in database
- This has been fixed - now email is sent FIRST, then user is saved

**Current Behavior**:
- Email is sent BEFORE saving user to database
- If email fails, user is NOT saved
- Error is returned to client with helpful message

### Still Having Issues?

1. **Check Resend Logs**:
   - Go to Resend Dashboard → Logs
   - Look for failed email attempts
   - Check error messages and delivery status

2. **Verify API Key Permissions**:
   - Ensure API key has "Send Email" permissions
   - Check if API key is rate-limited or suspended

3. **Contact Resend Support**:
   - Email: support@resend.com
   - Include your domain name and API key (masked)
   - Describe the error you're seeing

### Quick Reference

- **Resend Dashboard**: https://resend.com
- **Domain Management**: https://resend.com/domains
- **API Keys**: https://resend.com/api-keys
- **Email Logs**: https://resend.com/emails
- **Documentation**: https://resend.com/docs

---

**Last Updated**: 2025-01-27
**Domain**: dolabb.com
**FROM Email**: no-reply@dolabb.com
**API Key**: re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ

