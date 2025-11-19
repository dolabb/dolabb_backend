# Deployment Checklist - Resend Email Configuration

## ⚠️ CRITICAL: Why You're Still Getting the Old Error

The error mentions `anaspirzada510@gmail.com` which is from your **OLD Resend account**. This means:

1. **Old API key is still being used** - Even though you updated environment variables in Render, the service might not have been redeployed
2. **Default fallback values** - The code had old API key as default (now fixed)
3. **Code changes not deployed** - The fix to prevent user saving on email failure needs to be deployed

## ✅ What We Fixed in Code

1. ✅ Removed old API key defaults from `settings.py`
2. ✅ Added validation in production settings to require environment variables
3. ✅ Fixed order: Email sent BEFORE saving user (prevents orphaned records)
4. ✅ Updated `setup.py` with new API key

## 🔧 What YOU Need to Do NOW

### Step 1: Verify Environment Variables in Render

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Select your **Web Service** (dolabb-backend)
3. Go to **Environment** tab
4. **Verify these exact values**:

```
RESEND_API_KEY=re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ
RESEND_FROM_EMAIL=no-reply@dolabb.com
```

**⚠️ IMPORTANT**: 
- Check for typos
- Ensure there are NO extra spaces
- Ensure the values match EXACTLY above

### Step 2: REDEPLOY Your Service

**This is CRITICAL!** Environment variable changes require a redeploy:

1. In Render Dashboard → Your Web Service
2. Click **Manual Deploy** → **Deploy latest commit**
   - OR click **Redeploy** if you see that option
3. Wait for deployment to complete (usually 2-5 minutes)
4. Check deployment logs for any errors

### Step 3: Verify Domain in Resend

1. Go to **Resend Dashboard**: https://resend.com/domains
2. Check that `dolabb.com` shows as **✅ Verified** (green checkmark)
3. If not verified:
   - Click on the domain
   - Add DNS records (SPF, DKIM, DMARC) to your domain provider
   - Wait for verification (5 min - 48 hours)
   - See `RESEND_DNS_SETUP_GUIDE.md` for details

### Step 4: Test After Deployment

1. Wait for deployment to complete
2. Test the signup endpoint:
   ```bash
   POST https://dolabb-backend.onrender.com/api/auth/signup/
   ```
3. **Expected behavior**:
   - ✅ If email succeeds: User is saved, OTP sent
   - ✅ If email fails: User is **NOT** saved, error returned

## 🔍 How to Verify Current Configuration

### Option 1: Check Render Logs

1. Go to Render Dashboard → Your Web Service → **Logs**
2. Look for startup messages
3. If you see errors about missing `RESEND_API_KEY`, the env var isn't set

### Option 2: Use the Verification Script

After deploying, you can add a temporary endpoint to check config:

```python
# Add to authentication/views.py temporarily
@api_view(['GET'])
@permission_classes([AllowAny])
def check_config(request):
    from django.conf import settings
    return Response({
        'api_key_set': bool(settings.RESEND_API_KEY),
        'api_key_preview': f"{settings.RESEND_API_KEY[:4]}...{settings.RESEND_API_KEY[-4:]}" if settings.RESEND_API_KEY else None,
        'from_email': settings.RESEND_FROM_EMAIL,
        'is_old_key': 're_GpJeG6m2' in (settings.RESEND_API_KEY or ''),
    })
```

## 🐛 Troubleshooting

### Still Getting Old Error After Redeploy?

1. **Check if environment variables are actually set**:
   - Render Dashboard → Environment → Verify values
   - Look for typos or extra spaces

2. **Check deployment logs**:
   - Look for any errors during startup
   - Check if the service started successfully

3. **Verify you're using production settings**:
   - Check `DJANGO_SETTINGS_MODULE` environment variable
   - Should be: `dolabb_backend.settings_production`

4. **Clear Render cache** (if applicable):
   - Sometimes Render caches environment variables
   - Try redeploying again

### User Still Being Saved Despite Error?

This means the **new code isn't deployed yet**. The fix we made sends email BEFORE saving user. You need to:

1. **Push the latest code to GitHub** (already done ✅)
2. **Redeploy on Render** (you need to do this)

### Domain Not Verified?

1. Go to Resend Dashboard → Domains
2. Check DNS records are added correctly
3. Wait for DNS propagation (can take up to 48 hours)
4. Click "Verify" button again

## 📋 Quick Checklist

- [ ] Environment variables set correctly in Render
- [ ] `RESEND_API_KEY` = `re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ`
- [ ] `RESEND_FROM_EMAIL` = `no-reply@dolabb.com`
- [ ] Service redeployed after env var changes
- [ ] Domain `dolabb.com` verified in Resend dashboard
- [ ] DNS records (SPF, DKIM, DMARC) added to domain provider
- [ ] Tested signup endpoint after deployment
- [ ] Verified user is NOT saved if email fails

## 🚨 Common Mistakes

1. **Setting env vars but not redeploying** - Changes only take effect after redeploy
2. **Typos in environment variables** - Double-check spelling
3. **Using old API key** - Make sure it's the new one: `re_h7DXEMec_...`
4. **Domain not verified** - Even if DNS is set, domain must show as "Verified" in Resend
5. **Testing with account owner's email** - Test with a different email address

## 📞 Still Having Issues?

1. Check Render deployment logs for errors
2. Check Resend dashboard → Logs for email delivery status
3. Verify domain status in Resend dashboard
4. Ensure all environment variables are set correctly

---

**Last Updated**: 2025-01-27
**API Endpoint**: https://dolabb-backend.onrender.com/api/auth/signup/
**Expected API Key**: re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ
**Expected FROM Email**: no-reply@dolabb.com

