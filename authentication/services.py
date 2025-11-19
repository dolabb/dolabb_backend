"""
Authentication services
"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from authentication.models import Admin, User, Affiliate, TempUser
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
    def user_signup(full_name, email, phone, password, confirm_password, country_code=None, dial_code=None, profile_image_url=None, role='seller'):
        """User signup - stores in temp_users until OTP verification"""
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Check if user already exists in users collection
        if User.objects(email=email).first():
            raise ValueError("User with this email already exists")
        
        # Check if user already exists in temp_users collection
        existing_temp = TempUser.objects(email=email).first()
        if existing_temp:
            # Update existing temp user instead of creating new one
            temp_user = existing_temp
            temp_user.full_name = full_name
            temp_user.phone = phone
            temp_user.country_code = country_code
            temp_user.dial_code = dial_code
            temp_user.profile_image = profile_image_url
            temp_user.role = role
            temp_user.set_password(password)
        else:
            # Create new temp user
            temp_user = TempUser(
                full_name=full_name,
                email=email,
                phone=phone,
                country_code=country_code,
                dial_code=dial_code,
                profile_image=profile_image_url,
                role=role,
                status='pending_verification'
            )
            temp_user.set_password(password)
        
        # Generate OTP
        otp_code = temp_user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        
        # Send email BEFORE saving to database
        # If email fails, user won't be saved
        try:
            send_otp_email(email, otp_code, full_name)
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to send OTP email. Please check your email configuration. Error: {str(e)}")
        
        # Only save temp user if email was sent successfully
        temp_user.save()
        
        # Don't generate token yet - wait for OTP verification
        return temp_user, otp_code
    
    @staticmethod
    def user_verify_otp(email, otp):
        """Verify user OTP - moves data from temp_users to users collection"""
        # Check temp_users first
        temp_user = TempUser.objects(email=email).first()
        if not temp_user:
            # Check if user is already verified
            user = User.objects(email=email).first()
            if user:
                raise ValueError("User is already verified")
            raise ValueError("User not found")
        
        if not temp_user.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        # Check if user already exists in users (shouldn't happen, but safety check)
        if User.objects(email=email).first():
            # Delete temp entry and raise error
            temp_user.delete()
            raise ValueError("User already exists in verified users")
        
        # Generate username from email
        username = email.split('@')[0]
        counter = 1
        while User.objects(username=username).first():
            username = f"{email.split('@')[0]}{counter}"
            counter += 1
        
        # Create user in main users collection
        user = User(
            full_name=temp_user.full_name,
            email=temp_user.email,
            phone=temp_user.phone,
            country_code=temp_user.country_code,
            dial_code=temp_user.dial_code,
            profile_image=temp_user.profile_image,
            role=temp_user.role,
            password_hash=temp_user.password_hash  # Copy hashed password
        )
        user.username = username
        user.status = 'active'
        
        try:
            # Save user to main collection
            user.save()
            
            # Delete temp entry after successful save
            temp_user.delete()
            
            # Generate token after successful verification
            token = JWTService.generate_token(user.id, 'user', user.email, user.role)
            
            return user, token
        except Exception as e:
            # Rollback: if user save fails, don't delete temp entry
            # If user was saved but temp delete fails, that's okay (temp will expire)
            raise Exception(f"Failed to complete verification: {str(e)}")
    
    @staticmethod
    def user_login(email, password):
        """User login"""
        # First check if user exists in temp_users (pending verification)
        temp_user = TempUser.objects(email=email).first()
        if temp_user:
            if temp_user.check_password(password):
                raise ValueError("Verification pending. Please verify your email with the OTP sent to your email address.")
            else:
                raise ValueError("Invalid credentials")
        
        # Check verified users
        user = User.objects(email=email).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        
        if user.status != 'active':
            raise ValueError("Account is suspended or deactivated")
        
        token = JWTService.generate_token(user.id, 'user', user.email, user.role)
        return user, token
    
    @staticmethod
    def user_resend_otp(email):
        """Resend OTP for user - works with temp_users"""
        # Check temp_users first
        temp_user = TempUser.objects(email=email).first()
        if not temp_user:
            # Check if user is already verified
            user = User.objects(email=email).first()
            if user:
                raise ValueError("User is already verified. Please login instead.")
            raise ValueError("User not found")
        
        # Generate new OTP
        otp_code = temp_user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        temp_user.save()
        
        send_otp_email(email, otp_code, temp_user.full_name)
        return otp_code
    
    @staticmethod
    def user_forgot_password(email):
        """User forgot password - only verified users can reset password"""
        # Check if user exists in temp_users (not verified)
        temp_user = TempUser.objects(email=email).first()
        if temp_user:
            raise ValueError("Account verification pending. Please verify your email first before resetting password.")
        
        # Only verified users can reset password
        user = User.objects(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        # Validate user status
        if user.status != 'active':
            raise ValueError("Account is suspended or deactivated. Cannot reset password.")
        
        otp_code = user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        user.save()
        
        send_otp_email(email, otp_code, user.full_name)
        return otp_code
    
    @staticmethod
    def user_reset_password(email, otp, new_password, confirm_password):
        """User reset password - only verified users can reset password"""
        if new_password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Check if user exists in temp_users (not verified)
        temp_user = TempUser.objects(email=email).first()
        if temp_user:
            raise ValueError("Account verification pending. Please verify your email first before resetting password.")
        
        # Only verified users can reset password
        user = User.objects(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        # Validate user status
        if user.status != 'active':
            raise ValueError("Account is suspended or deactivated. Cannot reset password.")
        
        if not user.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        try:
            user.set_password(new_password)
            user.otp = None
            user.save()
            return user
        except Exception as e:
            # Rollback: password change failed, don't clear OTP
            raise Exception(f"Failed to reset password: {str(e)}")
    
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
    def resend_otp_combined(email, user_type):
        """Combined resend OTP for admin, user, and affiliate"""
        user_type = user_type.lower()
        
        if user_type == 'admin':
            otp = AuthService.admin_resend_otp(email)
            return {'otp': otp}
        elif user_type == 'user':
            otp = AuthService.user_resend_otp(email)
            return {'otp': otp}
        elif user_type == 'affiliate':
            # Affiliate resend OTP (if needed, implement similar to admin)
            affiliate = Affiliate.objects(email=email).first()
            if not affiliate:
                raise ValueError("Affiliate not found")
            otp_code = affiliate.generate_otp(settings.OTP_EXPIRY_SECONDS)
            affiliate.save()
            send_otp_email(email, otp_code, affiliate.full_name)
            return {'otp': otp_code}
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

