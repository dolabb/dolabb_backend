"""
Script to check Resend configuration
Run this to verify your Resend API key and email settings
"""
import os
import sys
from django.conf import settings

def check_resend_config():
    """Check Resend configuration"""
    print("=" * 60)
    print("Resend Configuration Check")
    print("=" * 60)
    
    # Check environment variables
    api_key = os.getenv('RESEND_API_KEY', '')
    from_email = os.getenv('RESEND_FROM_EMAIL', '')
    
    print(f"\n1. Environment Variables:")
    print(f"   RESEND_API_KEY: {'✅ Set' if api_key else '❌ NOT SET'}")
    if api_key:
        # Show first and last 4 characters for security
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        print(f"      Value: {masked_key}")
        # Check if it's the old key
        if 're_GpJeG6m2' in api_key:
            print(f"      ⚠️  WARNING: This appears to be the OLD API key!")
        elif 're_h7DXEMec' in api_key:
            print(f"      ✅ This appears to be the NEW API key")
    
    print(f"   RESEND_FROM_EMAIL: {'✅ Set' if from_email else '❌ NOT SET'}")
    if from_email:
        print(f"      Value: {from_email}")
        if from_email == 'onboarding@resend.dev':
            print(f"      ⚠️  WARNING: Using default Resend email (not verified domain)")
        elif '@dolabb.com' in from_email:
            print(f"      ✅ Using dolabb.com domain")
        else:
            print(f"      ⚠️  WARNING: Not using dolabb.com domain")
    
    # Check Django settings
    print(f"\n2. Django Settings:")
    try:
        django_api_key = settings.RESEND_API_KEY
        django_from_email = settings.RESEND_FROM_EMAIL
        
        print(f"   RESEND_API_KEY: {'✅ Set' if django_api_key else '❌ NOT SET'}")
        if django_api_key:
            masked_key = f"{django_api_key[:4]}...{django_api_key[-4:]}" if len(django_api_key) > 8 else "***"
            print(f"      Value: {masked_key}")
            if 're_GpJeG6m2' in django_api_key:
                print(f"      ⚠️  WARNING: Using OLD API key as default!")
        
        print(f"   RESEND_FROM_EMAIL: {'✅ Set' if django_from_email else '❌ NOT SET'}")
        if django_from_email:
            print(f"      Value: {django_from_email}")
            if django_from_email == 'onboarding@resend.dev':
                print(f"      ⚠️  WARNING: Using default Resend email!")
    except Exception as e:
        print(f"   ❌ Error loading Django settings: {e}")
    
    # Recommendations
    print(f"\n3. Recommendations:")
    issues = []
    
    if not api_key or 're_GpJeG6m2' in api_key:
        issues.append("❌ Update RESEND_API_KEY to: re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ")
    
    if not from_email or from_email == 'onboarding@resend.dev':
        issues.append("❌ Update RESEND_FROM_EMAIL to: no-reply@dolabb.com")
    
    if '@dolabb.com' not in from_email:
        issues.append("⚠️  Ensure RESEND_FROM_EMAIL uses dolabb.com domain")
    
    if issues:
        for issue in issues:
            print(f"   {issue}")
        print(f"\n   Steps to fix:")
        print(f"   1. Go to Render Dashboard → Your Web Service → Environment")
        print(f"   2. Update RESEND_API_KEY to: re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ")
        print(f"   3. Update RESEND_FROM_EMAIL to: no-reply@dolabb.com")
        print(f"   4. Save and REDEPLOY your service")
        print(f"   5. Verify domain is verified in Resend: https://resend.com/domains")
    else:
        print(f"   ✅ Configuration looks good!")
        print(f"   ⚠️  If still getting errors, ensure:")
        print(f"      - Domain dolabb.com is verified in Resend dashboard")
        print(f"      - DNS records are properly configured")
        print(f"      - Service has been redeployed after env var changes")
    
    print("\n" + "=" * 60)
    
    return len(issues) == 0

if __name__ == '__main__':
    # Setup Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dolabb_backend.settings')
    django.setup()
    
    success = check_resend_config()
    sys.exit(0 if success else 1)

