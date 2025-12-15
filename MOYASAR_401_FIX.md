# Moyasar 401 Unauthorized Error - Fix Guide

## Problem

After deploying the payment verification fix, you're now getting a **401 Unauthorized** error:

```
error: "Failed to verify payment status: 401 Client Error: Unauthorized for url: https://api.moyasar.com/v1/payments/..."
```

## Root Cause

The `MOYASAR_SECRET_KEY` environment variable is either:
1. **Not set** in Render production environment
2. **Incorrect/Invalid** - wrong key or expired key
3. **Wrong format** - not starting with `sk_live_` or `sk_test_`

## Solution

### Step 1: Verify Environment Variable in Render

1. Go to your Render Dashboard: https://dashboard.render.com
2. Navigate to your Web Service (dolabb-backend-2vsj)
3. Click on **Environment** tab
4. Check if `MOYASAR_SECRET_KEY` exists:
   - If **NOT present**: Add it
   - If **present**: Verify it's correct

### Step 2: Get Your Moyasar Secret Key

1. Log in to Moyasar Dashboard: https://moyasar.com/dashboard
2. Go to **Settings** → **API Keys**
3. Copy your **Secret Key** (should start with `sk_live_` for production)
4. Make sure you're using the **LIVE** key, not the test key

### Step 3: Set Environment Variable in Render

1. In Render Dashboard → Your Web Service → Environment
2. Add or update:
   ```
   MOYASAR_SECRET_KEY=sk_live_xxxxxxxxxxxxx
   ```
   (Replace `xxxxxxxxxxxxx` with your actual secret key)

3. Also verify these are set:
   ```
   MOYASAR_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
   MOYASAR_API_URL=https://api.moyasar.com/v1/payments
   ```

### Step 4: Redeploy

After setting the environment variable:
1. Render will automatically redeploy, OR
2. Manually trigger a redeploy from Render Dashboard

### Step 5: Test

After redeployment, test a payment:
- The verification should now work
- You should see successful verification instead of 401 error

## Code Changes Made

I've improved error handling in `payments/services.py` to:
1. ✅ Validate secret key format (must start with `sk_live_` or `sk_test_`)
2. ✅ Provide clearer error messages for 401 errors
3. ✅ Give specific guidance on what to check

## Verification Checklist

- [ ] `MOYASAR_SECRET_KEY` is set in Render environment variables
- [ ] Secret key starts with `sk_live_` (production) or `sk_test_` (testing)
- [ ] Secret key matches the one in Moyasar dashboard
- [ ] `MOYASAR_PUBLISHABLE_KEY` is also set
- [ ] `MOYASAR_API_URL` is set (or uses default)
- [ ] Service has been redeployed after setting variables

## Common Issues

### Issue: "Key not found"
- **Solution**: Make sure the environment variable name is exactly `MOYASAR_SECRET_KEY` (case-sensitive)

### Issue: "401 Unauthorized" persists
- **Solution**: 
  1. Double-check the key in Moyasar dashboard
  2. Ensure you're using LIVE key for production (not test key)
  3. Verify no extra spaces or quotes in the environment variable value
  4. Redeploy the service

### Issue: "Invalid format"
- **Solution**: Secret key must start with `sk_live_` or `sk_test_`. Check the key format in Moyasar dashboard.

## Next Steps

1. **Set the environment variable** in Render (most important!)
2. **Redeploy** the service
3. **Test** a payment to verify it works
4. **Monitor logs** to ensure no more 401 errors

## Testing

After fixing, you should see:
- ✅ Successful payment verification (200 OK)
- ✅ Payment status returned correctly
- ✅ Webhook processing succeeds
- ✅ Success page redirect works

Instead of:
- ❌ 401 Unauthorized errors
- ❌ Verification failures
- ❌ Redirect to messages route

