"""
Authentication models using mongoengine
"""
from mongoengine import Document, StringField, EmailField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, BooleanField
from datetime import datetime, timedelta
import bcrypt
import secrets


class OTPEmbedded(EmbeddedDocument):
    """OTP embedded document"""
    code = StringField(required=True)
    expires_at = DateTimeField(required=True)


class Admin(Document):
    """Admin model"""
    name = StringField(required=True, max_length=200)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    role = StringField(default='admin', max_length=50)
    profile_image = StringField()
    otp = EmbeddedDocumentField(OTPEmbedded)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'admins',
        'indexes': ['email']
    }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_otp(self, expiry_seconds=300):
        """Generate OTP"""
        code = str(secrets.randbelow(10000)).zfill(4)
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        self.otp = OTPEmbedded(code=code, expires_at=expires_at)
        return code
    
    def verify_otp(self, code):
        """Verify OTP"""
        if not self.otp:
            return False
        if datetime.utcnow() > self.otp.expires_at:
            return False
        return self.otp.code == code
    
    @property
    def is_authenticated(self):
        """Required by Django REST Framework"""
        return True
    
    @property
    def is_authenticated(self):
        """Required by Django REST Framework"""
        return True


class User(Document):
    """User model for buyers and sellers"""
    full_name = StringField(required=True, max_length=200)
    username = StringField(required=True, unique=True, max_length=100)
    email = EmailField(required=True, unique=True)
    phone = StringField(max_length=20)
    country_code = StringField(max_length=10)
    dial_code = StringField(max_length=10)
    password_hash = StringField(required=True)
    profile_image = StringField()
    bio = StringField(max_length=500)
    location = StringField(max_length=200)
    role = StringField(required=True, choices=['buyer', 'seller'], default='buyer')
    status = StringField(choices=['active', 'suspended', 'deactivated'], default='active')
    otp = EmbeddedDocumentField(OTPEmbedded)
    join_date = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': ['email', 'username', 'phone']
    }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_otp(self, expiry_seconds=300):
        """Generate OTP"""
        code = str(secrets.randbelow(10000)).zfill(4)
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        self.otp = OTPEmbedded(code=code, expires_at=expires_at)
        return code
    
    def verify_otp(self, code):
        """Verify OTP"""
        if not self.otp:
            return False
        if datetime.utcnow() > self.otp.expires_at:
            return False
        return self.otp.code == code
    
    @property
    def is_authenticated(self):
        """Required by Django REST Framework"""
        return True
    
    @property
    def is_authenticated(self):
        """Required by Django REST Framework"""
        return True


class Affiliate(Document):
    """Affiliate model"""
    full_name = StringField(required=True, max_length=200)
    email = EmailField(required=True, unique=True)
    phone = StringField(required=True, max_length=20)
    country_code = StringField(max_length=10)
    password_hash = StringField(required=True)
    affiliate_code = StringField(required=True, unique=True, max_length=50)
    commission_rate = StringField(default='0')
    code_usage_count = StringField(default='0')
    total_earnings = StringField(default='0')
    pending_earnings = StringField(default='0')
    paid_earnings = StringField(default='0')
    status = StringField(choices=['active', 'deactivated'], default='active')
    last_activity = DateTimeField(default=datetime.utcnow)
    bank_name = StringField(max_length=200)
    account_number = StringField(max_length=100)
    iban = StringField(max_length=100)
    account_holder_name = StringField(max_length=200)
    profile_image = StringField()
    otp = EmbeddedDocumentField(OTPEmbedded)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'affiliates',
        'indexes': ['email', 'affiliate_code', 'phone']
    }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_otp(self, expiry_seconds=300):
        """Generate OTP"""
        code = str(secrets.randbelow(10000)).zfill(4)
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        self.otp = OTPEmbedded(code=code, expires_at=expires_at)
        return code
    
    def verify_otp(self, code):
        """Verify OTP"""
        if not self.otp:
            return False
        if datetime.utcnow() > self.otp.expires_at:
            return False
        return self.otp.code == code
    
    @property
    def is_authenticated(self):
        """Required by Django REST Framework"""
        return True

