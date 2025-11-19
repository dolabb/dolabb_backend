"""
Authentication services
"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from authentication.models import Admin, User, Affiliate
from authentication.email_service import send_otp_email


class JWTService:
    """JWT token service"""
    
    @staticmethod
    def generate_token(user_id, user_type='user', email='', role=''):
        """Generate JWT token"""
        payload = {
            'user_id': str(user_id),
            'user_type': user_type,  # 'admin', 'user', 'affiliate'
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(days=int(settings.JWT_EXPIRES_IN.replace('d', ''))),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
        return token
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def admin_signup(name, email, password, confirm_password, profile_image_url=None):
        """Admin signup"""
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        if Admin.objects(email=email).first():
            raise ValueError("Admin with this email already exists")
        
        admin = Admin(name=name, email=email)
        if profile_image_url:
            admin.profile_image = profile_image_url
        admin.set_password(password)
        otp_code = admin.generate_otp(settings.OTP_EXPIRY_SECONDS)
        
        # Send email BEFORE saving to database
        # If email fails, admin won't be saved
        try:
            send_otp_email(email, otp_code, name)
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to send OTP email. Please check your email configuration. Error: {str(e)}")
        
        # Only save admin if email was sent successfully
        admin.save()
        
        return admin, otp_code
    
    @staticmethod
    def admin_login(email, password):
        """Admin login"""
        admin = Admin.objects(email=email).first()
        if not admin or not admin.check_password(password):
            raise ValueError("Invalid credentials")
        
        token = JWTService.generate_token(admin.id, 'admin', admin.email, admin.role)
        return admin, token
    
    @staticmethod
    def admin_resend_otp(email):
        """Resend OTP for admin"""
        admin = Admin.objects(email=email).first()
        if not admin:
            raise ValueError("Admin not found")
        
        otp_code = admin.generate_otp(settings.OTP_EXPIRY_SECONDS)
        admin.save()
        
        send_otp_email(email, otp_code, admin.name)
        return otp_code
    
    @staticmethod
    def admin_forgot_password(email):
        """Admin forgot password"""
        admin = Admin.objects(email=email).first()
        if not admin:
            raise ValueError("Admin not found")
        
        otp_code = admin.generate_otp(settings.OTP_EXPIRY_SECONDS)
        admin.save()
        
        send_otp_email(email, otp_code, admin.name)
        return otp_code
    
    @staticmethod
    def admin_verify_otp(email, otp):
        """Verify admin OTP"""
        admin = Admin.objects(email=email).first()
        if not admin:
            raise ValueError("Admin not found")
        
        if not admin.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        # Clear OTP after verification
        admin.otp = None
        admin.save()
        
        # Generate token after successful verification
        token = JWTService.generate_token(admin.id, 'admin', admin.email, admin.role)
        
        return admin, token
    
    @staticmethod
    def admin_reset_password(email, otp, new_password, confirm_password):
        """Admin reset password"""
        if new_password != confirm_password:
            raise ValueError("Passwords do not match")
        
        admin = Admin.objects(email=email).first()
        if not admin:
            raise ValueError("Admin not found")
        
        if not admin.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        admin.set_password(new_password)
        admin.otp = None
        admin.save()
        
        return admin
    
    @staticmethod
    def user_signup(full_name, email, phone, password, confirm_password, country_code=None, dial_code=None, profile_image_url=None, role='buyer'):
        """User signup"""
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        if User.objects(email=email).first():
            raise ValueError("User with this email already exists")
        
        # Generate username from email
        username = email.split('@')[0]
        counter = 1
        while User.objects(username=username).first():
            username = f"{email.split('@')[0]}{counter}"
            counter += 1
        
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            country_code=country_code,
            dial_code=dial_code,
            profile_image=profile_image_url,
            role=role
        )
        user.username = username
        user.set_password(password)
        otp_code = user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        
        # Send email BEFORE saving to database
        # If email fails, user won't be saved
        try:
            send_otp_email(email, otp_code, full_name)
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to send OTP email. Please check your email configuration. Error: {str(e)}")
        
        # Only save user if email was sent successfully
        user.save()
        
        # Don't generate token yet - wait for OTP verification
        return user, otp_code
    
    @staticmethod
    def user_verify_otp(email, otp):
        """Verify user OTP"""
        user = User.objects(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        if not user.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        # Clear OTP after verification
        user.otp = None
        user.save()
        
        # Generate token after successful verification
        token = JWTService.generate_token(user.id, 'user', user.email, user.role)
        
        return user, token
    
    @staticmethod
    def user_login(email, password):
        """User login"""
        user = User.objects(email=email).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        
        if user.status != 'active':
            raise ValueError("Account is suspended or deactivated")
        
        token = JWTService.generate_token(user.id, 'user', user.email, user.role)
        return user, token
    
    @staticmethod
    def user_resend_otp(email):
        """Resend OTP for user"""
        user = User.objects(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        otp_code = user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        user.save()
        
        send_otp_email(email, otp_code, user.full_name)
        return otp_code
    
    @staticmethod
    def user_forgot_password(email):
        """User forgot password"""
        user = User.objects(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        otp_code = user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        user.save()
        
        send_otp_email(email, otp_code, user.full_name)
        return otp_code
    
    @staticmethod
    def user_reset_password(email, otp, new_password, confirm_password):
        """User reset password"""
        if new_password != confirm_password:
            raise ValueError("Passwords do not match")
        
        user = User.objects(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        if not user.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        user.set_password(new_password)
        user.otp = None
        user.save()
        
        return user
    
    @staticmethod
    def affiliate_verify_otp(email, otp):
        """Verify affiliate OTP"""
        affiliate = Affiliate.objects(email=email).first()
        if not affiliate:
            raise ValueError("Affiliate not found")
        
        if not affiliate.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        # Clear OTP after verification
        affiliate.otp = None
        affiliate.save()
        
        # Generate token after successful verification
        token = JWTService.generate_token(affiliate.id, 'affiliate', affiliate.email, 'affiliate')
        
        return affiliate, token
    
    @staticmethod
    def affiliate_signup(full_name, email, phone, password, country_code, bank_name, account_number, iban=None, account_holder_name=None, profile_image_url=None):
        """Affiliate signup"""
        if Affiliate.objects(email=email).first():
            raise ValueError("Affiliate with this email already exists")
        
        # Generate affiliate code
        import random
        import string
        affiliate_code = f"AFF-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        while Affiliate.objects(affiliate_code=affiliate_code).first():
            affiliate_code = f"AFF-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        affiliate = Affiliate(
            full_name=full_name,
            email=email,
            phone=phone,
            country_code=country_code,
            bank_name=bank_name,
            account_number=account_number,
            iban=iban,
            account_holder_name=account_holder_name or full_name,
            affiliate_code=affiliate_code,
            profile_image=profile_image_url
        )
        affiliate.set_password(password)
        # Generate OTP for affiliate verification
        otp_code = affiliate.generate_otp(settings.OTP_EXPIRY_SECONDS)
        
        # Send email BEFORE saving to database
        # If email fails, affiliate won't be saved
        try:
            send_otp_email(email, otp_code, full_name)
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to send OTP email. Please check your email configuration. Error: {str(e)}")
        
        # Only save affiliate if email was sent successfully
        affiliate.save()
        
        # Don't generate token yet - wait for OTP verification
        return affiliate, otp_code
    
    @staticmethod
    def verify_otp_combined(email, otp, user_type):
        """Combined OTP verification for admin, user, and affiliate"""
        user_type = user_type.lower()
        
        if user_type == 'admin':
            admin, token = AuthService.admin_verify_otp(email, otp)
            return {
                'user_type': 'admin',
                'user': {
                    'id': str(admin.id),
                    'name': admin.name,
                    'email': admin.email,
                    'role': admin.role
                },
                'token': token
            }
        elif user_type == 'user':
            user, token = AuthService.user_verify_otp(email, otp)
            return {
                'user_type': 'user',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'profile_image': user.profile_image or '',
                    'role': user.role
                },
                'token': token
            }
        elif user_type == 'affiliate':
            affiliate, token = AuthService.affiliate_verify_otp(email, otp)
            return {
                'user_type': 'affiliate',
                'affiliate': {
                    'id': str(affiliate.id),
                    'full_name': affiliate.full_name,
                    'email': affiliate.email,
                    'phone': affiliate.phone,
                    'affiliate_code': affiliate.affiliate_code,
                    'status': affiliate.status
                },
                'token': token
            }
        else:
            raise ValueError(f"Invalid user_type. Must be 'admin', 'user', or 'affiliate'")
    
    @staticmethod
    def affiliate_login(email, password):
        """Affiliate login"""
        affiliate = Affiliate.objects(email=email).first()
        if not affiliate or not affiliate.check_password(password):
            raise ValueError("Invalid credentials")
        
        if affiliate.status != 'active':
            raise ValueError("Affiliate account is deactivated")
        
        token = JWTService.generate_token(affiliate.id, 'affiliate', affiliate.email, 'affiliate')
        return affiliate, token

