"""
Authentication views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from authentication.services import AuthService, JWTService
from authentication.serializers import (
    AdminSignupSerializer, AdminLoginSerializer, AdminForgotPasswordSerializer, AdminResetPasswordSerializer,
    UserSignupSerializer, UserLoginSerializer, UserForgotPasswordSerializer, UserResetPasswordSerializer,
    AffiliateSignupSerializer, AffiliateLoginSerializer, AffiliateForgotPasswordSerializer, AffiliateResetPasswordSerializer,
    UserProfileSerializer, VerifyOTPSerializer,
    ResendOTPSerializer, ContactFormSerializer
)
from authentication.models import User
from authentication.otp_views import verify_otp, admin_verify_otp, user_verify_otp, affiliate_verify_otp
from products.services import ProductService


# Admin Authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_signup(request):
    """Admin signup"""
    serializer = AdminSignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin, otp = AuthService.admin_signup(
            serializer.validated_data['name'],
            serializer.validated_data['email'],
            serializer.validated_data['password'],
            serializer.validated_data['confirm_password'],
            serializer.validated_data.get('profile_image_url'),
            request
        )
        return Response({
            'success': True,
            'message': 'Admin registered successfully. OTP sent to email. Please verify OTP to complete registration.',
            'otp': otp,
            'admin': {
                'id': str(admin.id),
                'name': admin.name,
                'email': admin.email,
                'role': admin.role
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Admin login"""
    serializer = AdminLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin, token = AuthService.admin_login(
            serializer.validated_data['email'],
            serializer.validated_data['password']
        )
        return Response({
            'success': True,
            'admin': {
                'id': str(admin.id),
                'name': admin.name,
                'email': admin.email,
                'role': admin.role
            },
            'token': token
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_forgot_password(request):
    """Admin forgot password"""
    serializer = AdminForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp = AuthService.admin_forgot_password(serializer.validated_data['email'])
        return Response({
            'success': True,
            'message': 'Reset OTP sent to email',
            'otp': otp
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_reset_password(request):
    """Admin reset password"""
    serializer = AdminResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin = AuthService.admin_reset_password(
            serializer.validated_data['email'],
            serializer.validated_data['otp'],
            serializer.validated_data['new_password'],
            serializer.validated_data['confirm_password']
        )
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def admin_logout(request):
    """Admin logout - invalidates token on client side"""
    # Since JWT tokens are stateless, we can't invalidate them server-side
    # without implementing a token blacklist. For now, this endpoint serves
    # as a signal to the client to remove the token.
    # In production, consider implementing token blacklist or refresh tokens.
    return Response({
        'success': True,
        'message': 'Logged out successfully. Please remove the token from client storage.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_resend_otp(request):
    """Resend OTP for admin signup"""
    serializer = AdminForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp = AuthService.admin_resend_otp(serializer.validated_data['email'])
        return Response({
            'success': True,
            'message': 'OTP resent successfully',
            'otp': otp
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_resend_forgot_password_otp(request):
    """Resend OTP for admin forgot password"""
    serializer = AdminForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp = AuthService.admin_forgot_password(serializer.validated_data['email'])
        return Response({
            'success': True,
            'message': 'Reset OTP resent successfully',
            'otp': otp
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# User Authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
    """User signup"""
    serializer = UserSignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get language from request (frontend can send it from localStorage for guest users)
        language = request.data.get('language') or request.data.get('preferredLanguage')
        if language and language not in ['en', 'ar']:
            language = None  # Invalid language, will default to 'en'
        
        temp_user, otp = AuthService.user_signup(
            serializer.validated_data['full_name'],
            serializer.validated_data['username'],
            serializer.validated_data['email'],
            serializer.validated_data['phone'],
            serializer.validated_data['password'],
            serializer.validated_data['confirm_password'],
            serializer.validated_data.get('country_code'),
            serializer.validated_data.get('dial_code'),
            serializer.validated_data.get('profile_image_url'),
            serializer.validated_data.get('role', 'buyer'),
            request,
            language=language
        )
        return Response({
            'success': True,
            'message': 'User registered successfully. OTP sent to email. Please verify OTP to complete registration.',
            'user': {
                'id': str(temp_user.id),
                'username': temp_user.username,
                'email': temp_user.email,
                'phone': temp_user.phone,
                'profile_image': temp_user.profile_image or '',
                'role': temp_user.role,
                'status': temp_user.status
            },
            'otp': otp
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login"""
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get either username or email from validated data
        identifier = serializer.validated_data.get('username') or serializer.validated_data.get('email')
        user, token = AuthService.user_login(
            identifier,
            serializer.validated_data['password']
        )
        
        # Get saved products for the user
        saved_products = ProductService.get_saved_products(str(user.id))
        
        return Response({
            'success': True,
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
                'language': getattr(user, 'language', 'en'),  # Default to 'en' if not set
                'join_date': user.join_date.isoformat() if user.join_date else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'token': token,
            'savedProducts': saved_products
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_forgot_password(request):
    """User forgot password - accepts optional language parameter from frontend"""
    serializer = UserForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get language from request (frontend can send it from localStorage for guest users)
        language = request.data.get('language') or request.data.get('preferredLanguage')
        if language and language not in ['en', 'ar']:
            language = None  # Invalid language, will use user's preference
        
        otp = AuthService.user_forgot_password(serializer.validated_data['email'], language=language)
        return Response({
            'success': True,
            'message': 'Reset OTP sent to email',
            'otp': otp
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_reset_password(request):
    """User reset password"""
    serializer = UserResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = AuthService.user_reset_password(
            serializer.validated_data['email'],
            serializer.validated_data['otp'],
            serializer.validated_data['new_password'],
            serializer.validated_data['confirm_password']
        )
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile_by_id(request, user_id):
    """Get user profile by user ID (public endpoint)"""
    try:
        from bson import ObjectId
        from products.services import ReviewService
        
        # Convert user_id to ObjectId if needed
        try:
            if isinstance(user_id, str):
                user_obj_id = ObjectId(user_id)
            else:
                user_obj_id = user_id
        except (Exception, ValueError):
            return Response({'success': False, 'error': 'Invalid user ID format'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects(id=user_obj_id).first()
        if not user:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Helper function to safely get date
        def get_date_safe(obj, *attrs):
            for attr in attrs:
                val = getattr(obj, attr, None)
                if val:
                    try:
                        return val.isoformat() if hasattr(val, 'isoformat') else str(val)
                    except:
                        return str(val)
            return ''
        
        # Helper function to safely get attribute
        def safe_get(obj, attr, default=''):
            try:
                val = getattr(obj, attr, default)
                return val if val is not None else default
            except:
                return default
        
        # Helper function to normalize profile image URL
        def normalize_image_url(url):
            """Normalize image URL to ensure it's accessible"""
            if not url or url == '':
                return ''
            # If URL is already absolute, return as is
            if url.startswith('http://') or url.startswith('https://'):
                return url
            # If URL is relative, make it absolute using current request
            if url.startswith('/'):
                return request.build_absolute_uri(url)
            # If URL doesn't start with /, add /media/ prefix if it's a media file
            if 'uploads' in url or 'profiles' in url:
                return request.build_absolute_uri(f'/media/{url}')
            return url
        
        user_data = {
            'id': str(user.id),
            'username': safe_get(user, 'username'),
            'email': safe_get(user, 'email'),
            'phone': safe_get(user, 'phone'),
            'full_name': safe_get(user, 'full_name'),
            'profile_image': normalize_image_url(safe_get(user, 'profile_image') or ''),
            'bio': safe_get(user, 'bio') or '',
            'location': safe_get(user, 'location') or '',
            'role': safe_get(user, 'role', 'buyer'),
            'joined_date': get_date_safe(user, 'join_date', 'created_at'),
        }
        
        # Add seller rating and review count if user is a seller
        if safe_get(user, 'role', 'buyer') == 'seller':
            try:
                rating_stats = ReviewService.get_seller_rating_stats(str(user.id))
                user_data['rating'] = {
                    'averageRating': rating_stats['average_rating'],
                    'totalReviews': rating_stats['total_reviews'],
                    'ratingDistribution': rating_stats['rating_distribution']
                }
            except Exception:
                # If rating service fails, set defaults
                user_data['rating'] = {
                    'averageRating': 0.0,
                    'totalReviews': 0,
                    'ratingDistribution': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
                }
        
        return Response({
            'success': True,
            'user': user_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        from django.conf import settings
        return Response({
            'success': False, 
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PATCH', 'PUT'])
def get_profile(request):
    """Get or update user profile"""
    # Handle GET request - return profile
    if request.method == 'GET':
        try:
            user = request.user
            
            if not user or not hasattr(user, 'id'):
                return Response({'success': False, 'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Helper function to safely get date
            def get_date_safe(obj, *attrs):
                for attr in attrs:
                    val = getattr(obj, attr, None)
                    if val:
                        try:
                            return val.isoformat() if hasattr(val, 'isoformat') else str(val)
                        except:
                            return str(val)
                return ''
            
            # Helper function to safely get attribute
            def safe_get(obj, attr, default=''):
                try:
                    val = getattr(obj, attr, default)
                    return val if val is not None else default
                except:
                    return default
            
            # Helper function to normalize profile image URL
            def normalize_image_url(url):
                """Normalize image URL to ensure it's accessible"""
                if not url or url == '':
                    return ''
                # If URL is already absolute, return as is
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                # If URL is relative, make it absolute using current request
                if url.startswith('/'):
                    return request.build_absolute_uri(url)
                # If URL doesn't start with /, add /media/ prefix if it's a media file
                if 'uploads' in url or 'profiles' in url:
                    return request.build_absolute_uri(f'/media/{url}')
                return url
            
            # Handle different user types
            if hasattr(user, 'username'):  # Regular User
                user_data = {
                    'id': str(user.id),
                    'username': safe_get(user, 'username'),
                    'email': safe_get(user, 'email'),
                    'phone': safe_get(user, 'phone'),
                    'full_name': safe_get(user, 'full_name'),
                    'profile_image': normalize_image_url(safe_get(user, 'profile_image') or ''),
                    'bio': safe_get(user, 'bio') or '',
                    'location': safe_get(user, 'location') or '',
                    'shipping_address': safe_get(user, 'shipping_address') or '',
                    'zip_code': safe_get(user, 'zip_code') or '',
                    'house_number': safe_get(user, 'house_number') or '',
                    'joined_date': get_date_safe(user, 'join_date', 'created_at'),
                    'role': safe_get(user, 'role', 'buyer'),
                    'language': getattr(user, 'language', 'en')  # Default to 'en' if not set
                }
                
                # Add seller rating and review count if user is a seller
                if safe_get(user, 'role', 'buyer') == 'seller':
                    try:
                        from products.services import ReviewService
                        rating_stats = ReviewService.get_seller_rating_stats(str(user.id))
                        user_data['rating'] = {
                            'averageRating': rating_stats['average_rating'],
                            'totalReviews': rating_stats['total_reviews'],
                            'ratingDistribution': rating_stats['rating_distribution']
                        }
                    except Exception:
                        # If rating service fails, set defaults
                        user_data['rating'] = {
                            'averageRating': 0.0,
                            'totalReviews': 0,
                            'ratingDistribution': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
                        }
                
                return Response({
                    'success': True,
                    'user': user_data
                }, status=status.HTTP_200_OK)
            
            elif hasattr(user, 'name'):  # Admin
                return Response({
                    'success': True,
                    'user': {
                        'id': str(user.id),
                        'username': '',
                        'email': safe_get(user, 'email'),
                        'phone': '',
                        'full_name': safe_get(user, 'name'),
                        'profile_image': normalize_image_url(safe_get(user, 'profile_image') or ''),
                        'bio': '',
                        'location': '',
                        'joined_date': get_date_safe(user, 'created_at'),
                        'role': safe_get(user, 'role', 'admin')
                    }
                }, status=status.HTTP_200_OK)
            
            elif hasattr(user, 'full_name') and hasattr(user, 'affiliate_code'):  # Affiliate
                # Format earnings and usage count as numbers
                total_earnings = float(user.total_earnings) if hasattr(user, 'total_earnings') and user.total_earnings else 0.0
                pending_earnings = float(user.pending_earnings) if hasattr(user, 'pending_earnings') and user.pending_earnings else 0.0
                paid_earnings = float(user.paid_earnings) if hasattr(user, 'paid_earnings') and user.paid_earnings else 0.0
                code_usage_count = int(user.code_usage_count) if hasattr(user, 'code_usage_count') and user.code_usage_count else 0
                
                return Response({
                    'success': True,
                    'user': {
                        'id': str(user.id),
                        'username': '',
                        'email': safe_get(user, 'email'),
                        'phone': safe_get(user, 'phone'),
                        'full_name': safe_get(user, 'full_name'),
                        'profile_image': normalize_image_url(safe_get(user, 'profile_image') or ''),
                        'bio': '',
                        'location': '',
                        'joined_date': get_date_safe(user, 'created_at'),
                        'role': 'affiliate',
                        'affiliate_code': safe_get(user, 'affiliate_code'),
                        'totalEarnings': total_earnings,
                        'pendingEarnings': pending_earnings,
                        'paidEarnings': paid_earnings,
                        'codeUsageCount': code_usage_count,
                        'availableBalance': pending_earnings
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({'success': False, 'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
        except AttributeError as e:
            import traceback
            from django.conf import settings
            return Response({
                'success': False, 
                'error': f'Attribute error: {str(e)}',
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            import traceback
            from django.conf import settings
            return Response({
                'success': False, 
                'error': f'Server error: {str(e)}',
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Handle PATCH/PUT request - update profile
    elif request.method in ['PATCH', 'PUT']:
        try:
            user = request.user
            data = request.data
            
            if not user or not hasattr(user, 'id'):
                return Response({'success': False, 'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if hasattr(user, 'username'):  # Regular User
                if 'full_name' in data:
                    user.full_name = data['full_name']
                if 'username' in data:
                    user.username = data['username']
                if 'bio' in data:
                    user.bio = data['bio']
                if 'location' in data:
                    user.location = data['location']
                if 'profile_image' in data:
                    # Process base64 image if needed
                    processed_image = AuthService.process_profile_image(data['profile_image'], request)
                    user.profile_image = processed_image if processed_image else data['profile_image']
                if 'shipping_address' in data:
                    user.shipping_address = data['shipping_address']
                if 'shippingAddress' in data:
                    user.shipping_address = data['shippingAddress']
                if 'zip_code' in data:
                    user.zip_code = data['zip_code']
                if 'zipCode' in data:
                    user.zip_code = data['zipCode']
                if 'house_number' in data:
                    user.house_number = data['house_number']
                if 'houseNumber' in data:
                    user.house_number = data['houseNumber']
                
                # Role update - allow switching between buyer and seller
                if 'role' in data:
                    new_role = data['role'].lower()
                    if new_role in ['buyer', 'seller']:
                        user.role = new_role
                    else:
                        return Response({
                            'success': False,
                            'error': 'Invalid role. Must be "buyer" or "seller"'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Bank/Payment fields (optional)
                bank_details_updated = False
                if 'bank_name' in data:
                    user.bank_name = data['bank_name']
                    bank_details_updated = True
                if 'bankName' in data:
                    user.bank_name = data['bankName']
                    bank_details_updated = True
                if 'account_number' in data:
                    user.account_number = data['account_number']
                    bank_details_updated = True
                if 'accountNumber' in data:
                    user.account_number = data['accountNumber']
                    bank_details_updated = True
                if 'iban' in data:
                    user.iban = data['iban']
                    bank_details_updated = True
                if 'IBAN' in data:
                    user.iban = data['IBAN']
                    bank_details_updated = True
                if 'account_holder_name' in data:
                    user.account_holder_name = data['account_holder_name']
                    bank_details_updated = True
                if 'accountHolderName' in data:
                    user.account_holder_name = data['accountHolderName']
                    bank_details_updated = True
                
                # Language preference
                if 'language' in data:
                    language = data['language']
                    if language in ['en', 'ar']:
                        user.language = language
                elif 'preferredLanguage' in data:
                    language = data['preferredLanguage']
                    if language in ['en', 'ar']:
                        user.language = language
                
                user.save()
                
                # Send notification if bank details were updated
                if bank_details_updated:
                    try:
                        from notifications.notification_helper import NotificationHelper
                        if user.role == 'seller':
                            NotificationHelper.send_bank_payment_setup_completed(str(user.id))
                        else:
                            NotificationHelper.send_buyer_bank_payment_setup_completed(str(user.id))
                    except Exception as e:
                        print(f"Error sending bank setup notification: {str(e)}")
                
                # Helper functions for response
                def get_date_safe(obj, *attrs):
                    for attr in attrs:
                        val = getattr(obj, attr, None)
                        if val:
                            try:
                                return val.isoformat() if hasattr(val, 'isoformat') else str(val)
                            except:
                                return str(val)
                    return ''
                
                def safe_get(obj, attr, default=''):
                    try:
                        val = getattr(obj, attr, default)
                        return val if val is not None else default
                    except:
                        return default
                
                def normalize_image_url(url):
                    if not url or url == '':
                        return ''
                    if url.startswith('http://') or url.startswith('https://'):
                        return url
                    if url.startswith('/'):
                        return request.build_absolute_uri(url)
                    if 'uploads' in url or 'profiles' in url:
                        return request.build_absolute_uri(f'/media/{url}')
                    return url
                
                serializer = UserProfileSerializer({
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'full_name': user.full_name,
                    'profile_image': normalize_image_url(user.profile_image or ''),
                    'bio': user.bio or '',
                    'location': user.location or '',
                    'shipping_address': user.shipping_address or '',
                    'zip_code': user.zip_code or '',
                    'house_number': user.house_number or '',
                    'joined_date': user.join_date,
                    'role': user.role,
                    'language': getattr(user, 'language', 'en')
                })
                return Response({'success': True, 'user': serializer.data}, status=status.HTTP_200_OK)
            
            return Response({'success': False, 'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            import traceback
            from django.conf import settings
            return Response({
                'success': False,
                'error': f'Server error: {str(e)}',
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # If method is not GET, PATCH, or PUT
    else:
        return Response({
            'success': False,
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['PUT', 'PATCH'])
def update_profile(request):
    """Update user profile"""
    user = request.user
    data = request.data
    
    if hasattr(user, 'username'):  # User
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'username' in data:
            user.username = data['username']
        if 'bio' in data:
            user.bio = data['bio']
        if 'location' in data:
            user.location = data['location']
        if 'profile_image' in data:
            # Process base64 image if needed
            processed_image = AuthService.process_profile_image(data['profile_image'], request)
            user.profile_image = processed_image if processed_image else data['profile_image']
        if 'shipping_address' in data:
            user.shipping_address = data['shipping_address']
        if 'shippingAddress' in data:
            user.shipping_address = data['shippingAddress']
        if 'zip_code' in data:
            user.zip_code = data['zip_code']
        if 'zipCode' in data:
            user.zip_code = data['zipCode']
        if 'house_number' in data:
            user.house_number = data['house_number']
        if 'houseNumber' in data:
            user.house_number = data['houseNumber']
        
        # Role update - allow switching between buyer and seller
        if 'role' in data:
            new_role = data['role'].lower()
            if new_role in ['buyer', 'seller']:
                user.role = new_role
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid role. Must be "buyer" or "seller"'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Bank/Payment fields (optional)
        bank_details_updated = False
        if 'bank_name' in data:
            user.bank_name = data['bank_name']
            bank_details_updated = True
        if 'bankName' in data:
            user.bank_name = data['bankName']
            bank_details_updated = True
        if 'account_number' in data:
            user.account_number = data['account_number']
            bank_details_updated = True
        if 'accountNumber' in data:
            user.account_number = data['accountNumber']
            bank_details_updated = True
        if 'iban' in data:
            user.iban = data['iban']
            bank_details_updated = True
        if 'IBAN' in data:
            user.iban = data['IBAN']
            bank_details_updated = True
        if 'account_holder_name' in data:
            user.account_holder_name = data['account_holder_name']
            bank_details_updated = True
        if 'accountHolderName' in data:
            user.account_holder_name = data['accountHolderName']
            bank_details_updated = True
        
        # Language preference
        if 'language' in data:
            language = data['language']
            if language in ['en', 'ar']:
                user.language = language
        elif 'preferredLanguage' in data:
            language = data['preferredLanguage']
            if language in ['en', 'ar']:
                user.language = language
        
        user.save()
        
        # Send notification if bank details were updated
        if bank_details_updated:
            try:
                from notifications.notification_helper import NotificationHelper
                if user.role == 'seller':
                    NotificationHelper.send_bank_payment_setup_completed(str(user.id))
                else:
                    NotificationHelper.send_buyer_bank_payment_setup_completed(str(user.id))
            except Exception as e:
                print(f"Error sending bank setup notification: {str(e)}")
        
        serializer = UserProfileSerializer({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'full_name': user.full_name,
            'profile_image': user.profile_image or '',
            'bio': user.bio or '',
            'location': user.location or '',
            'shipping_address': user.shipping_address or '',
            'zip_code': user.zip_code or '',
            'house_number': user.house_number or '',
            'joined_date': user.join_date,
            'role': user.role,
            'language': getattr(user, 'language', 'en')
        })
        return Response({'success': True, 'user': serializer.data}, status=status.HTTP_200_OK)
    
    return Response({'success': False, 'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_language(request):
    """Update user language preference - works with or without token"""
    try:
        language = request.data.get('language') or request.data.get('preferredLanguage')
        
        if not language:
            return Response({'success': False, 'error': 'Language is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if language not in ['en', 'ar']:
            return Response({'success': False, 'error': 'Invalid language. Must be "en" or "ar"'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is authenticated (has id attribute = real database model, not AnonymousUser)
        if hasattr(request, 'user') and request.user and hasattr(request.user, 'id'):
            # User is authenticated - update language in database
            user = request.user
            user.language = language
            user.save()
            
            return Response({
                'success': True,
                'message': f'Language updated to {language}',
                'language': user.language,
                'authenticated': True
            }, status=status.HTTP_200_OK)
        else:
            # User is not authenticated - just return the language (frontend can store it locally)
            return Response({
                'success': True,
                'message': f'Language preference set to {language}',
                'language': language,
                'authenticated': False
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Affiliate Authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def affiliate_signup(request):
    """Affiliate signup"""
    serializer = AffiliateSignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        affiliate, otp = AuthService.affiliate_signup(
            serializer.validated_data['full_name'],
            serializer.validated_data['email'],
            serializer.validated_data['phone'],
            serializer.validated_data['password'],
            serializer.validated_data['country_code'],
            serializer.validated_data.get('profile_image_url'),
            request
        )
        return Response({
            'success': True,
            'message': 'Affiliate registered successfully. OTP sent to email. Please verify OTP to complete registration.',
            'affiliate': {
                'id': str(affiliate.id),
                'full_name': affiliate.full_name,
                'email': affiliate.email,
                'phone': affiliate.phone,
                'affiliate_code': affiliate.affiliate_code,
                'profile_image': affiliate.profile_image or '',
                'total_earnings': affiliate.total_earnings,
                'total_commissions': affiliate.total_earnings,
                'code_usage_count': affiliate.code_usage_count,
                'status': affiliate.status,
                'created_at': affiliate.created_at.isoformat()
            },
            'otp': otp
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def affiliate_login(request):
    """Affiliate login"""
    serializer = AffiliateLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        affiliate, token = AuthService.affiliate_login(
            serializer.validated_data['email'],
            serializer.validated_data['password']
        )
        # Format earnings and usage count as numbers
        total_earnings = float(affiliate.total_earnings) if affiliate.total_earnings else 0.0
        pending_earnings = float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0
        paid_earnings = float(affiliate.paid_earnings) if affiliate.paid_earnings else 0.0
        code_usage_count = int(affiliate.code_usage_count) if affiliate.code_usage_count else 0
        
        return Response({
            'success': True,
            'affiliate': {
                'id': str(affiliate.id),
                'full_name': affiliate.full_name,
                'email': affiliate.email,
                'phone': affiliate.phone,
                'affiliate_code': affiliate.affiliate_code,
                'totalEarnings': total_earnings,
                'totalCommissions': total_earnings,
                'pendingEarnings': pending_earnings,
                'paidEarnings': paid_earnings,
                'codeUsageCount': code_usage_count,
                'availableBalance': pending_earnings,  # Available balance = pending earnings
                'status': affiliate.status
            },
            'token': token
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def affiliate_forgot_password(request):
    """Affiliate forgot password"""
    serializer = AffiliateForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp = AuthService.affiliate_forgot_password(serializer.validated_data['email'])
        return Response({
            'success': True,
            'message': 'Reset OTP sent to email',
            'otp': otp
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def affiliate_reset_password(request):
    """Affiliate reset password"""
    serializer = AffiliateResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        affiliate = AuthService.affiliate_reset_password(
            serializer.validated_data['email'],
            serializer.validated_data['otp'],
            serializer.validated_data['new_password'],
            serializer.validated_data['confirm_password']
        )
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_form(request):
    """Handle contact form submissions"""
    serializer = ContactFormSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from notifications.email_templates import send_notification_email
        
        # Get form data
        full_name = serializer.validated_data['full_name']
        email = serializer.validated_data['email']
        phone = serializer.validated_data.get('phone', '')
        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']
        
        # Create email content
        email_subject = f"Contact Form: {subject}"
        
        # Format email message
        email_message = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1f2937; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">
                New Contact Form Submission
            </h2>
            
            <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 10px 0;"><strong style="color: #1f2937;">Full Name:</strong> {full_name}</p>
                <p style="margin: 10px 0;"><strong style="color: #1f2937;">Email:</strong> <a href="mailto:{email}" style="color: #3b82f6;">{email}</a></p>
        """
        
        if phone:
            email_message += f'<p style="margin: 10px 0;"><strong style="color: #1f2937;">Phone:</strong> <a href="tel:{phone}" style="color: #3b82f6;">{phone}</a></p>'
        
        email_message += f"""
                <p style="margin: 10px 0;"><strong style="color: #1f2937;">Subject:</strong> {subject}</p>
            </div>
            
            <div style="background-color: #ffffff; padding: 20px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                <h3 style="color: #1f2937; margin-top: 0;">Message:</h3>
                <p style="white-space: pre-wrap; color: #4b5563;">{message}</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                <p>This email was sent from the contact form on dolabb.com</p>
                <p>You can reply directly to this email to respond to {full_name} at {email}</p>
            </div>
        </div>
        """
        
        # Send email to contact@dolabb.com
        send_notification_email(
            email='contact@dolabb.com',
            notification_title=email_subject,
            notification_message=email_message,
            notification_type='info',
            user_name='Dolabb Team',
            language='en'
        )
        
        return Response({
            'success': True,
            'message': 'Thank you for contacting us! We have received your message and will get back to you soon.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import logging
        logging.error(f"Error sending contact form email: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to send your message. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

