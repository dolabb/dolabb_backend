# Verify Moyasar Keys in Render - Step by Step

## Your Keys (for reference)

- **Secret Key**: `sk_live_xxxxxxxxxxxxx`
- **Public Key**: `pk_live_xxxxxxxxxxxxx`

## ✅ Verification Steps

### Step 1: Check Render Environment Variables

1. Go to: https://dashboard.render.com
2. Click on your service: `dolabb-backend-2vsj`
3. Click on **Environment** tab
4. Look for these variables:

#### Check MOYASAR_SECRET_KEY

- [ ] Variable name is exactly: `MOYASAR_SECRET_KEY` (case-sensitive, no spaces)
- [ ] Value is exactly: `sk_live_xxxxxxxxxxxxx` (your actual secret key)
- [ ] **NO quotes** around the value (not `"sk_live_..."`)
- [ ] **NO spaces** before or after the value
- [ ] **NO line breaks** in the value

#### Check MOYASAR_PUBLISHABLE_KEY

- [ ] Variable name is exactly: `MOYASAR_PUBLISHABLE_KEY` (case-sensitive, no
      spaces)
- [ ] Value is exactly: `pk_live_xxxxxxxxxxxxx` (your actual publishable key)
- [ ] **NO quotes** around the value
- [ ] **NO spaces** before or after the value

### Step 2: Common Issues

#### ❌ Wrong Format (with quotes)

```
MOYASAR_SECRET_KEY="sk_live_xxxxxxxxxxxxx"
```

**Fix**: Remove the quotes

#### ❌ Wrong Format (with spaces)

```
MOYASAR_SECRET_KEY = sk_live_xxxxxxxxxxxxx
```

**Fix**: Remove spaces around `=`

#### ❌ Wrong Format (missing characters)

```
MOYASAR_SECRET_KEY=sk_live_xxxxxxxxxxxxx (incomplete - missing last character)
```

**Fix**: Check if last character is missing

### Step 3: After Updating Variables

1. **Save** the environment variables
2. **Redeploy** the service (Render should auto-redeploy, or manually trigger)
3. **Wait** for deployment to complete
4. **Test** a payment

### Step 4: Check Logs After Payment

After making a test payment, check Render logs:

1. Go to Render Dashboard → Your Service → **Logs**
2. Look for these log messages:

#### ✅ Success (Key is correct)

```
Using MOYASAR_SECRET_KEY starting with: sk_live_xxxxxxxxxxxxx...
Calling Moyasar API: https://api.moyasar.com/v1/payments/...
✅ Verified payment status from Moyasar: paid
```

#### ❌ Failure (Key is wrong/missing)

```
Using MOYASAR_SECRET_KEY starting with: None... (length: 0)
```

OR

```
Moyasar API returned 401 Unauthorized. Secret key starts with: sk_live_xxxxxxxxxxxxx...
```

### Step 5: Verify Key in Moyasar Dashboard

1. Go to: https://moyasar.com/dashboard
2. Login to your account
3. Go to **Settings** → **API Keys**
4. Verify the **Secret Key** matches your Render environment variable
5. Verify the **Publishable Key** matches your Render environment variable

### Step 6: Check Payment Account Match

**Important**: The payment ID must belong to the same Moyasar account as your
keys.

- If you're using test payments, make sure you're using **test keys**
  (`sk_test_...`)
- If you're using live payments, make sure you're using **live keys**
  (`sk_live_...`)
- The payment ID format should match: `00e5c80e-b56b-433a-970a-c2402ae34aff`
  (UUID format)

## Troubleshooting

### Issue: Still getting 401 after setting keys correctly

**Possible causes:**

1. **Service not redeployed** - Environment variables only take effect after
   redeploy
2. **Wrong account** - Payment ID belongs to different Moyasar account
3. **Key mismatch** - Key in Render doesn't match key in Moyasar dashboard
4. **Cached values** - Old environment variables cached (redeploy fixes this)

**Solution:**

1. Double-check keys in Render match Moyasar dashboard exactly
2. Redeploy the service
3. Check logs to see what key is actually being used
4. Verify payment ID belongs to the same account

### Issue: Key shows as None in logs

**Cause**: Environment variable not set or not being read

**Solution:**

1. Check variable name is exactly `MOYASAR_SECRET_KEY` (case-sensitive)
2. Check there are no extra spaces or quotes
3. Save and redeploy

## Quick Test

After setting keys correctly and redeploying:

1. Make a test payment
2. Check Render logs
3. Should see: `Using MOYASAR_SECRET_KEY starting with: sk_live_xxxxxxxxxxxxx...`
4. Should see: `✅ Verified payment status from Moyasar: paid`
5. Should NOT see: `401 Unauthorized`

## Summary

✅ **Keys look correct** in format ✅ **Code updated** to add logging and strip
whitespace ⚠️ **Verify** keys are set correctly in Render (no quotes, no spaces)
⚠️ **Redeploy** after setting/updating keys ✅ **Check logs** to see what key is
actually being used
