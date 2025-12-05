"""
Authentication services
"""
import jwt
import base64
import os
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from authentication.models import Admin, User, Affiliate, TempUser
from authentication.email_service import send_otp_email
from products.services import ProductService


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
    def process_profile_image(image_data, request=None):
        """Convert base64 profile image to URL by saving it to server"""
        if not image_data:
            return None
        
        # If already a URL, keep it as is
        if isinstance(image_data, str):
            if image_data.startswith('http://') or image_data.startswith('https://'):
                return image_data
            
            # Check if it's base64
            if image_data.startswith('data:image'):
                try:
                    # Extract base64 data
                    header, encoded = image_data.split(',', 1)
                    # Get file extension from header
                    if 'jpeg' in header or 'jpg' in header:
                        ext = '.jpg'
                    elif 'png' in header:
                        ext = '.png'
                    elif 'gif' in header:
                        ext = '.gif'
                    elif 'webp' in header:
                        ext = '.webp'
                    else:
                        ext = '.jpg'  # default
                    
                    # Decode base64
                    image_bytes = base64.b64decode(encoded)
                    
                    # Generate unique filename
                    unique_filename = f"{uuid.uuid4()}{ext}"
                    
                    # Try to upload to VPS if configured, otherwise use local storage
                    vps_enabled = getattr(settings, 'VPS_ENABLED', False)
                    
                    if vps_enabled:
                        # Upload to VPS
                        from storage.vps_helper import upload_file_to_vps
                        success, result = upload_file_to_vps(
                            image_bytes,
                            'uploads/profiles',
                            unique_filename
                        )
                        
                        if success:
                            import logging
                            logging.info(f"Profile image uploaded to VPS: {result}")
                            return result
                        else:
                            # Fallback to local storage if VPS upload fails
                            import logging
                            logging.warning(f"VPS upload failed, using local storage: {result}")
                    
                    # Local storage fallback
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'profiles')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    # Verify file was saved successfully
                    if not os.path.exists(file_path):
                        import logging
                        logging.error(f"File was not saved successfully: {file_path}")
                        return None
                    
                    # Generate URL - ensure consistent format
                    media_url = settings.MEDIA_URL.rstrip('/')
                    if not media_url.startswith('/'):
                        media_url = '/' + media_url
                    file_url = f"{media_url}/uploads/profiles/{unique_filename}"
                    
                    # Build absolute URL if request is available
                    if request:
                        # Use request to build absolute URL
                        absolute_url = request.build_absolute_uri(file_url)
                    else:
                        # Fallback to default if no request
                        absolute_url = f"https://dolabb-backend-2vsj.onrender.com{file_url}"
                    
                    # Log for debugging
                    import logging
                    logging.info(f"Profile image saved locally: {file_path}, URL: {absolute_url}")
                    
                    return absolute_url
                except Exception as e:
                    # If base64 processing fails, log error and return None
                    import logging
                    logging.error(f"Failed to process base64 profile image: {str(e)}")
                    return None
            else:
                # Not base64, not URL - might be a relative path, keep as is
                return image_data
        
        return None
    
    @staticmethod
    def admin_signup(name, email, password, confirm_password, profile_image_url=None, request=None):
        """Admin signup - Only one admin allowed"""
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Check if any admin already exists (only one admin allowed)
        existing_admin = Admin.objects().first()
        if existing_admin:
            raise ValueError("Admin account already exists. Only one admin is allowed.")
        
        if Admin.objects(email=email).first():
            raise ValueError("Admin with this email already exists")
        
        admin = Admin(name=name, email=email)
        if profile_image_url:
            # Process base64 image if needed
            processed_image_url = AuthService.process_profile_image(profile_image_url, request)
            admin.profile_image = processed_image_url if processed_image_url else profile_image_url
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
    def user_signup(full_name, username, email, phone, password, confirm_password, country_code=None, dial_code=None, profile_image_url=None, role='buyer', request=None, language=None):
        """User signup - stores in temp_users until OTP verification
        
        Args:
            language: Optional language preference ('en' or 'ar') for OTP email
        """
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Validate username uniqueness in users collection
        if User.objects(username=username).first():
            raise ValueError("Username already taken")
        
        # Validate username uniqueness in temp_users collection
        if TempUser.objects(username=username).first():
            raise ValueError("Username already taken")
        
        # Check if user already exists in users collection (by email)
        if User.objects(email=email).first():
            raise ValueError("User with this email already exists")
        
        # Process profile image if provided (convert base64 to URL if needed)
        processed_profile_image = None
        if profile_image_url:
            processed_profile_image = AuthService.process_profile_image(profile_image_url, request)
        
        # Get language preference: use provided language, or default to 'en'
        user_language = language if language in ['en', 'ar'] else 'en'
        
        # Check if user already exists in temp_users collection (by email)
        existing_temp = TempUser.objects(email=email).first()
        if existing_temp:
            # Update existing temp user instead of creating new one
            temp_user = existing_temp
            temp_user.full_name = full_name
            temp_user.username = username
            temp_user.phone = phone
            temp_user.country_code = country_code
            temp_user.dial_code = dial_code
            temp_user.profile_image = processed_profile_image if processed_profile_image else profile_image_url
            temp_user.role = role
            temp_user.set_password(password)
        else:
            # Create new temp user
            temp_user = TempUser(
                full_name=full_name,
                username=username,
                email=email,
                phone=phone,
                country_code=country_code,
                dial_code=dial_code,
                profile_image=processed_profile_image if processed_profile_image else profile_image_url,
                role=role,
                status='pending_verification'
            )
            temp_user.set_password(password)
        
        # Generate OTP
        otp_code = temp_user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        
        # Send email BEFORE saving to database
        # If email fails, user won't be saved
        try:
            send_otp_email(email, otp_code, full_name, user_language)
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
        
        # Check if username already exists in users (shouldn't happen, but safety check)
        if User.objects(username=temp_user.username).first():
            # Delete temp entry and raise error
            temp_user.delete()
            raise ValueError("Username already taken")
        
        # Create user in main users collection using username from temp_user
        user = User(
            full_name=temp_user.full_name,
            username=temp_user.username,
            email=temp_user.email,
            phone=temp_user.phone,
            country_code=temp_user.country_code,
            dial_code=temp_user.dial_code,
            profile_image=temp_user.profile_image,
            role=temp_user.role,
            password_hash=temp_user.password_hash  # Copy hashed password
        )
        user.status = 'active'
        
        try:
            # Save user to main collection
            user.save()
            
            # Delete temp entry after successful save
            temp_user.delete()
            
            # Generate token after successful verification
            token = JWTService.generate_token(user.id, 'user', user.email, user.role)
            
            # Send welcome email notification
            try:
                from notifications.notification_helper import NotificationHelper
                NotificationHelper.send_welcome_email(str(user.id))
            except Exception as e:
                import logging
                logging.error(f"Error sending welcome notification: {str(e)}")
            
            return user, token
        except Exception as e:
            # Rollback: if user save fails, don't delete temp entry
            # If user was saved but temp delete fails, that's okay (temp will expire)
            raise Exception(f"Failed to complete verification: {str(e)}")
    
    @staticmethod
    def user_login(identifier, password):
        """User login - accepts either username or email"""
        # Determine if identifier is username or email
        is_email = '@' in identifier
        
        # First check if user exists in temp_users (pending verification)
        if is_email:
            temp_user = TempUser.objects(email=identifier).first()
        else:
            temp_user = TempUser.objects(username=identifier).first()
        
        if temp_user:
            if temp_user.check_password(password):
                raise ValueError("Verification pending. Please verify your email with the OTP sent to your email address.")
            else:
                raise ValueError("Invalid credentials")
        
        # Check verified users by username or email
        if is_email:
            user = User.objects(email=identifier).first()
        else:
            user = User.objects(username=identifier).first()
        
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        
        if user.status != 'active':
            raise ValueError("Account is suspended or deactivated")
        
        token = JWTService.generate_token(user.id, 'user', user.email, user.role)
        return user, token
    
    @staticmethod
    def user_resend_otp(email, language=None):
        """Resend OTP for user - works with temp_users
        
        Args:
            email: User's email address
            language: Optional language preference ('en' or 'ar')
        """
        # Check temp_users first
        temp_user = TempUser.objects(email=email).first()
        if not temp_user:
            # Check if user is already verified
            user = User.objects(email=email).first()
            if user:
                raise ValueError("User is already verified. Please login instead.")
            raise ValueError("User not found")
        
        # Get language preference: use provided language, or default to 'en'
        user_language = language if language in ['en', 'ar'] else 'en'
        
        # Generate new OTP
        otp_code = temp_user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        temp_user.save()
        
        send_otp_email(email, otp_code, temp_user.full_name, user_language)
        return otp_code
    
    @staticmethod
    def user_forgot_password(email, language=None):
        """User forgot password - only verified users can reset password
        
        Args:
            email: User's email address
            language: Optional language preference ('en' or 'ar'). If not provided, uses user's saved preference.
        """
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
        
        # Get language preference: use provided language, or user's saved preference, or default to 'en'
        user_language = language
        if not user_language:
            user_language = getattr(user, 'language', 'en')
        if user_language not in ['en', 'ar']:
            user_language = 'en'
        
        otp_code = user.generate_otp(settings.OTP_EXPIRY_SECONDS)
        user.save()
        
        send_otp_email(email, otp_code, user.full_name, user_language)
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
        
        # Send welcome notification
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_welcome_to_affiliate_program(str(affiliate.id))
            
            # Check if bank details are missing
            if not affiliate.bank_name or not affiliate.account_number:
                NotificationHelper.send_affiliate_payment_details_needed(str(affiliate.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending affiliate notifications: {str(e)}")
        
        return affiliate, token
    
    @staticmethod
    def affiliate_forgot_password(email):
        """Affiliate forgot password"""
        affiliate = Affiliate.objects(email=email).first()
        if not affiliate:
            raise ValueError("Affiliate not found")
        
        # Validate affiliate status
        if affiliate.status != 'active':
            raise ValueError("Account is suspended or deactivated. Cannot reset password.")
        
        otp_code = affiliate.generate_otp(settings.OTP_EXPIRY_SECONDS)
        affiliate.save()
        
        send_otp_email(email, otp_code, affiliate.full_name)
        return otp_code
    
    @staticmethod
    def affiliate_reset_password(email, otp, new_password, confirm_password):
        """Affiliate reset password"""
        if new_password != confirm_password:
            raise ValueError("Passwords do not match")
        
        affiliate = Affiliate.objects(email=email).first()
        if not affiliate:
            raise ValueError("Affiliate not found")
        
        # Validate affiliate status
        if affiliate.status != 'active':
            raise ValueError("Account is suspended or deactivated. Cannot reset password.")
        
        if not affiliate.verify_otp(otp):
            raise ValueError("Invalid or expired OTP")
        
        try:
            affiliate.set_password(new_password)
            affiliate.otp = None
            affiliate.save()
            return affiliate
        except Exception as e:
            # Rollback: password change failed, don't clear OTP
            raise Exception(f"Failed to reset password: {str(e)}")
    
    @staticmethod
    def affiliate_signup(full_name, email, phone, password, country_code, bank_name, account_number, iban=None, account_holder_name=None, profile_image_url=None, request=None):
        """Affiliate signup"""
        if Affiliate.objects(email=email).first():
            raise ValueError("Affiliate with this email already exists")
        
        # Generate affiliate code
        import random
        import string
        affiliate_code = f"AFF-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        while Affiliate.objects(affiliate_code=affiliate_code).first():
            affiliate_code = f"AFF-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        # Process profile image if provided (convert base64 to URL if needed)
        processed_profile_image = None
        if profile_image_url:
            processed_profile_image = AuthService.process_profile_image(profile_image_url, request)
        
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
            profile_image=processed_profile_image if processed_profile_image else profile_image_url
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
                    'full_name': user.full_name,
                    'profile_image': user.profile_image or '',
                    'role': user.role,
                    'bio': user.bio or '',
                    'location': user.location or '',
                    'country_code': user.country_code or '',
                    'dial_code': user.dial_code or '',
                    'status': user.status,
                    'join_date': user.join_date.isoformat() if user.join_date else None,
                    'created_at': user.created_at.isoformat() if user.created_at else None
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
    def resend_otp_combined(email, user_type, language=None):
        """Combined resend OTP for admin, user, and affiliate
        
        Args:
            email: User's email address
            user_type: 'admin', 'user', or 'affiliate'
            language: Optional language preference ('en' or 'ar') for user type
        """
        user_type = user_type.lower()
        
        if user_type == 'admin':
            otp = AuthService.admin_resend_otp(email)
            return {'otp': otp}
        elif user_type == 'user':
            otp = AuthService.user_resend_otp(email, language=language)
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

