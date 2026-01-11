# AWS S3 + CloudFront Setup Guide for Dolabb Backend

Complete guide to set up the fastest image upload and delivery system for your Django backend hosted on Render.

---

## Table of Contents

1. [Create AWS Account](#1-create-aws-account)
2. [Create S3 Bucket](#2-create-s3-bucket)
3. [Enable S3 Transfer Acceleration](#3-enable-s3-transfer-acceleration)
4. [Create CloudFront Distribution](#4-create-cloudfront-distribution)
5. [Create IAM User for Backend](#5-create-iam-user-for-backend)
6. [Render Environment Variables](#6-render-environment-variables)
7. [Test Your Setup](#7-test-your-setup)

---

## 1. Create AWS Account

### Step 1.1: Sign Up
1. Go to [https://aws.amazon.com](https://aws.amazon.com)
2. Click **"Create an AWS Account"**
3. Enter email, password, and account name
4. Choose **"Personal"** or **"Business"** account type
5. Enter payment information (credit card required, but free tier available)
6. Verify phone number
7. Select **"Basic Support - Free"** plan

### Step 1.2: Enable MFA (Recommended)
1. Go to **IAM** → **Security credentials**
2. Enable **Multi-factor authentication (MFA)**
3. Use Google Authenticator or Authy app

---

## 2. Create S3 Bucket

### Step 2.1: Create Bucket
1. Go to **S3** service in AWS Console
2. Click **"Create bucket"**
3. Configure:
   ```
   Bucket name: dolabb-media-production
   AWS Region: Choose closest to your users (e.g., eu-west-1 for Middle East/Europe)
   ```

### Step 2.2: Object Ownership
```
Select: ACLs disabled (recommended)
```

### Step 2.3: Block Public Access Settings
```
☐ Block all public access  (UNCHECK this)

Then check these individually:
☐ Block public access to buckets and objects granted through new ACLs
☐ Block public access to buckets and objects granted through any ACLs
☑ Block public access to buckets and objects granted through new public bucket or access point policies
☑ Block public and cross-account access to buckets and objects through any public bucket or access point policies
```

### Step 2.4: Bucket Versioning
```
Select: Disable (to save costs, enable if you need file history)
```

### Step 2.5: Default Encryption
```
Encryption type: Server-side encryption with Amazon S3 managed keys (SSE-S3)
Bucket Key: Enable
```

### Step 2.6: Click "Create bucket"

### Step 2.7: Configure CORS
1. Go to your bucket → **Permissions** tab
2. Scroll to **Cross-origin resource sharing (CORS)**
3. Click **Edit** and paste:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
        "AllowedOrigins": [
            "https://dolabb.com",
            "https://www.dolabb.com",
            "https://dolabb-frontend.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        "ExposeHeaders": ["ETag", "x-amz-meta-custom-header"],
        "MaxAgeSeconds": 3600
    }
]
```

4. Click **Save changes**

---

## 3. Enable S3 Transfer Acceleration

This makes uploads **up to 500% faster** for users far from your S3 region.

### Step 3.1: Enable Transfer Acceleration
1. Go to your bucket → **Properties** tab
2. Scroll to **Transfer acceleration**
3. Click **Edit**
4. Select **Enable**
5. Click **Save changes**

### Step 3.2: Note Your Accelerated Endpoint
```
Standard endpoint:     dolabb-media-production.s3.eu-west-1.amazonaws.com
Accelerated endpoint:  dolabb-media-production.s3-accelerate.amazonaws.com
```

---

## 4. Create CloudFront Distribution

CloudFront is the CDN that serves images from 450+ edge locations worldwide.

### Step 4.1: Create Distribution
1. Go to **CloudFront** service
2. Click **"Create distribution"**

### Step 4.2: Origin Settings
```
Origin domain: dolabb-media-production.s3.eu-west-1.amazonaws.com (select your bucket)
Origin path: (leave empty)
Name: dolabb-media-s3-origin
Origin access: Origin access control settings (recommended)
```

### Step 4.3: Create Origin Access Control (OAC)
1. Click **"Create control setting"**
2. Configure:
   ```
   Name: dolabb-media-oac
   Signing behavior: Sign requests (recommended)
   Origin type: S3
   ```
3. Click **Create**

### Step 4.4: Default Cache Behavior
```
Viewer protocol policy: Redirect HTTP to HTTPS
Allowed HTTP methods: GET, HEAD, OPTIONS
Cache policy: CachingOptimized (recommended)
Origin request policy: CORS-S3Origin
Response headers policy: SimpleCORS
```

### Step 4.5: Settings
```
Price class: Use all edge locations (best performance)
Alternate domain name (CNAME): media.dolabb.com (optional, requires SSL cert)
Default root object: (leave empty)
```

### Step 4.6: Click "Create distribution"

### Step 4.7: Update S3 Bucket Policy
After creating the distribution, AWS will show a banner to update bucket policy.

1. Click **"Copy policy"**
2. Go to S3 bucket → **Permissions** → **Bucket policy**
3. Paste the policy (it looks like this):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::dolabb-media-production/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
                }
            }
        }
    ]
}
```

### Step 4.8: Note Your CloudFront Domain
```
Distribution domain: d1234567890abc.cloudfront.net
Status: Wait until "Deployed" (takes 5-10 minutes)
```

---

## 5. Create IAM User for Backend

Create a dedicated user with minimal permissions for your Django backend.

### Step 5.1: Create Policy
1. Go to **IAM** → **Policies** → **Create policy**
2. Click **JSON** tab and paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::dolabb-media-production",
                "arn:aws:s3:::dolabb-media-production/*"
            ]
        },
        {
            "Sid": "CloudFrontInvalidation",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation"
            ],
            "Resource": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
    ]
}
```

3. Click **Next**
4. Name: `dolabb-media-policy`
5. Click **Create policy**

### Step 5.2: Create User
1. Go to **IAM** → **Users** → **Create user**
2. User name: `dolabb-backend-service`
3. Click **Next**
4. Select **Attach policies directly**
5. Search and select `dolabb-media-policy`
6. Click **Next** → **Create user**

### Step 5.3: Create Access Keys
1. Click on the user `dolabb-backend-service`
2. Go to **Security credentials** tab
3. Click **Create access key**
4. Select **Application running outside AWS**
5. Click **Next** → **Create access key**
6. **IMPORTANT: Download or copy these credentials immediately!**

```
Access key ID:     AKIA1234567890EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## 6. Render Environment Variables

Add these environment variables to your Render dashboard.

### Step 6.1: Go to Render Dashboard
1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Select your service
3. Go to **Environment** tab

### Step 6.2: Add These Variables

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA1234567890EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=eu-west-1

# S3 Configuration
AWS_S3_BUCKET_NAME=dolabb-media-production
AWS_S3_TRANSFER_ACCELERATION=true

# CloudFront Configuration
AWS_CLOUDFRONT_DOMAIN=d1234567890abc.cloudfront.net
AWS_CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC

# Storage Settings (disable VPS, enable S3)
USE_S3_STORAGE=true
VPS_ENABLED=false

# Image Optimization
IMAGE_OPTIMIZATION_ENABLED=true
IMAGE_MAX_WIDTH=1920
IMAGE_MAX_HEIGHT=1920
IMAGE_QUALITY=85
```

### Step 6.3: Variable Reference Table

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | IAM user access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key | `wJalr...` |
| `AWS_REGION` | S3 bucket region | `eu-west-1` |
| `AWS_S3_BUCKET_NAME` | Your S3 bucket name | `dolabb-media-production` |
| `AWS_S3_TRANSFER_ACCELERATION` | Enable fast uploads | `true` |
| `AWS_CLOUDFRONT_DOMAIN` | CloudFront distribution domain | `d123.cloudfront.net` |
| `AWS_CLOUDFRONT_DISTRIBUTION_ID` | For cache invalidation | `E1234567890ABC` |
| `USE_S3_STORAGE` | Enable S3 storage | `true` |
| `VPS_ENABLED` | Disable old VPS storage | `false` |

---

## 7. Test Your Setup

### Step 7.1: Test S3 Upload (AWS CLI)
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Test upload
echo "test" > test.txt
aws s3 cp test.txt s3://dolabb-media-production/test.txt

# Test accelerated upload
aws s3 cp test.txt s3://dolabb-media-production/test-accelerated.txt --endpoint-url https://s3-accelerate.amazonaws.com
```

### Step 7.2: Test CloudFront Delivery
```bash
# Wait for CloudFront deployment (5-10 minutes)
# Then access your file:
curl -I https://d1234567890abc.cloudfront.net/test.txt

# Should return:
# HTTP/2 200
# x-cache: Hit from cloudfront
```

### Step 7.3: Test from Your Backend
After implementing the code changes, test the upload endpoint:
```bash
curl -X POST https://your-render-app.onrender.com/api/auth/upload-image/ \
  -F "image=@test-image.jpg"
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           UPLOAD FLOW                                   │
│                                                                         │
│   Mobile/Web App                                                        │
│        │                                                                │
│        ▼                                                                │
│   Django Backend (Render)                                               │
│        │                                                                │
│        ├──► Generate Presigned URL                                      │
│        │                                                                │
│        ▼                                                                │
│   S3 Transfer Acceleration ──► S3 Bucket                               │
│   (Fastest upload path)        (dolabb-media-production)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          DELIVERY FLOW                                  │
│                                                                         │
│   Mobile/Web App                                                        │
│        │                                                                │
│        ▼                                                                │
│   CloudFront Edge Location (nearest to user)                           │
│        │                                                                │
│        ├── Cache HIT ──► Return immediately (10-30ms)                  │
│        │                                                                │
│        └── Cache MISS ──► Fetch from S3 ──► Cache ──► Return           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Expected Performance

| Metric | Before (GoDaddy VPS) | After (S3 + CloudFront) |
|--------|---------------------|-------------------------|
| Upload time (5MB image) | 3-8 seconds | **< 1 second** |
| First image load | 500-2000ms | **50-150ms** |
| Cached image load | 500-2000ms | **10-30ms** |
| Global availability | 1 server | **450+ edge locations** |
| Uptime SLA | ~99% | **99.99%** |

---

## Cost Estimate (Monthly)

For ~10GB storage and ~100GB CDN traffic:

| Service | Cost |
|---------|------|
| S3 Storage (10GB) | $0.23 |
| S3 Transfer Acceleration | $0.04/GB uploaded |
| CloudFront (100GB) | $8.50 |
| **Total** | **~$10-15/month** |

---

## Next Steps

After setting up AWS, I will implement the code changes in your Django backend:

1. Create `storage/s3_helper.py` - S3 upload functions
2. Update `authentication/image_views.py` - Use S3 instead of VPS
3. Update `dolabb_backend/settings.py` - Add AWS settings
4. Update `requirements.txt` - Add boto3 library

Let me know when you've completed the AWS setup and I'll implement the code!

---

## Troubleshooting

### "Access Denied" Error
- Check IAM policy has correct bucket ARN
- Verify bucket policy allows CloudFront access
- Ensure CORS is configured correctly

### "Slow Uploads"
- Verify Transfer Acceleration is enabled
- Check you're using the accelerated endpoint

### "Images Not Loading"
- Wait for CloudFront deployment (5-10 minutes)
- Check CloudFront distribution status is "Deployed"
- Verify bucket policy includes CloudFront OAC

### "CORS Error in Browser"
- Update CORS configuration with your frontend domains
- Clear browser cache and retry

---

## Security Checklist

- [ ] MFA enabled on AWS root account
- [ ] IAM user has minimal required permissions
- [ ] S3 bucket blocks public access (except via CloudFront)
- [ ] Access keys stored securely in Render environment variables
- [ ] CORS configured with specific domains (not `*`)
- [ ] CloudFront uses HTTPS only

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Author:** Kiro AI Assistant
