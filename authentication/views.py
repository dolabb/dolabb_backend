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
    AffiliateSignupSerializer, AffiliateLoginSerializer, UserProfileSerializer, VerifyOTPSerializer,
    ResendOTPSerializer
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
            serializer.validated_data.get('profile_image_url')
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


# User Authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
    """User signup"""
    serializer = UserSignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        temp_user, otp = AuthService.user_signup(
            serializer.validated_data['full_name'],
            serializer.validated_data['email'],
            serializer.validated_data['phone'],
            serializer.validated_data['password'],
            serializer.validated_data['confirm_password'],
            serializer.validated_data.get('country_code'),
            serializer.validated_data.get('dial_code'),
            serializer.validated_data.get('profile_image_url'),
            serializer.validated_data.get('role', 'seller')
        )
        return Response({
            'success': True,
            'message': 'User registered successfully. OTP sent to email. Please verify OTP to complete registration.',
            'user': {
                'id': str(temp_user.id),
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
        user, token = AuthService.user_login(
            serializer.validated_data['email'],
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
    """User forgot password"""
    serializer = UserForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp = AuthService.user_forgot_password(serializer.validated_data['email'])
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
def get_profile(request):
    """Get user profile"""
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
        
        # Handle different user types
        if hasattr(user, 'username'):  # Regular User
            return Response({
                'success': True,
                'user': {
                    'id': str(user.id),
                    'username': safe_get(user, 'username'),
                    'email': safe_get(user, 'email'),
                    'phone': safe_get(user, 'phone'),
                    'full_name': safe_get(user, 'full_name'),
                    'profile_image': safe_get(user, 'profile_image') or '',
                    'bio': safe_get(user, 'bio') or '',
                    'location': safe_get(user, 'location') or '',
                    'joined_date': get_date_safe(user, 'join_date', 'created_at'),
                    'role': safe_get(user, 'role', 'buyer')
                }
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
                    'profile_image': safe_get(user, 'profile_image') or '',
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
                    'profile_image': safe_get(user, 'profile_image') or '',
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


@api_view(['PUT'])
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
            user.profile_image = data['profile_image']
        user.save()
        
        serializer = UserProfileSerializer({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'full_name': user.full_name,
            'profile_image': user.profile_image or '',
            'bio': user.bio or '',
            'location': user.location or '',
            'joined_date': user.join_date,
            'role': user.role
        })
        return Response({'success': True, 'user': serializer.data}, status=status.HTTP_200_OK)
    
    return Response({'success': False, 'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)


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
            serializer.validated_data['bank_name'],
            serializer.validated_data['account_number'],
            serializer.validated_data.get('iban'),
            serializer.validated_data.get('account_holder_name'),
            serializer.validated_data.get('profile_image_url')
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
                'bank_details': {
                    'bank_name': affiliate.bank_name,
                    'account_number': affiliate.account_number,
                    'iban': affiliate.iban or '',
                    'account_holder_name': affiliate.account_holder_name
                },
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

