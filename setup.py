"""
Setup script for Dolabb Backend
"""
import os
import sys

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print(".env file already exists. Skipping...")
        return
    
    env_content = """# Resend (email OTP)
RESEND_API_KEY=re_h7DXEMec_PXna1zyChxx7W5GLHLCe9QLJ
RESEND_FROM_EMAIL=no-reply@dolabb.com

# MongoDB
MONGODB_CONNECTION_STRING=mongodb+srv://dolabb_admin:Farad2025%24@cluster0.0imvu6l.mongodb.net/dolabb_db?retryWrites=true&w=majority

# JWT
SECRET_KEY=your_jwt_secret_here
JWT_EXPIRES_IN=1d
OTP_EXPIRY_SECONDS=300
PAGE_DEFAULT_LIMIT=10

# Moyasar Payment Gateway
MOYASAR_PUBLIC_KEY=your_moyasar_public_key
MOYASAR_SECRET_KEY=your_moyasar_secret_key

# Redis (for WebSockets)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(".env file created successfully!")
    print("Please update the values in .env file with your actual credentials.")

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        r.ping()
        print("✓ Redis is running")
        return True
    except Exception as e:
        print("✗ Redis is not running. Please start Redis:")
        print("  Windows: Download and run Redis or use Docker")
        print("  Linux: sudo systemctl start redis")
        print("  Mac: brew services start redis")
        return False

def main():
    print("Dolabb Backend Setup")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Check Redis
    print("\nChecking Redis...")
    check_redis()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run migrations (if needed)")
    print("4. Start server: python manage.py runserver")

if __name__ == '__main__':
    main()

