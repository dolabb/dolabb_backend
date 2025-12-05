"""
OTP Verification views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from authentication.services import AuthService
from authentication.serializers import VerifyOTPSerializer, ResendOTPSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP - Combined endpoint for admin, user, and affiliate"""
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = AuthService.verify_otp_combined(
            serializer.validated_data['email'],
            serializer.validated_data['otp'],
            serializer.validated_data['user_type']
        )
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully',
            **result
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_verify_otp(request):
    """Verify Admin OTP"""
    serializer = VerifyOTPSerializer(data={**request.data, 'user_type': 'admin'})
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin, token = AuthService.admin_verify_otp(
            serializer.validated_data['email'],
            serializer.validated_data['otp']
        )
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully',
            'admin': {
                'id': str(admin.id),
                'name': admin.name,
                'email': admin.email,
                'role': admin.role,
                'profile_image': admin.profile_image or ''
            },
            'token': token
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_verify_otp(request):
    """Verify User OTP"""
    serializer = VerifyOTPSerializer(data={**request.data, 'user_type': 'user'})
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user, token = AuthService.user_verify_otp(
            serializer.validated_data['email'],
            serializer.validated_data['otp']
        )
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully',
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
            'token': token
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def affiliate_verify_otp(request):
    """Verify Affiliate OTP"""
    serializer = VerifyOTPSerializer(data={**request.data, 'user_type': 'affiliate'})
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        affiliate, token = AuthService.affiliate_verify_otp(
            serializer.validated_data['email'],
            serializer.validated_data['otp']
        )
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully',
            'affiliate': {
                'id': str(affiliate.id),
                'full_name': affiliate.full_name,
                'email': affiliate.email,
                'phone': affiliate.phone,
                'affiliate_code': affiliate.affiliate_code,
                'profile_image': affiliate.profile_image or '',
                'status': affiliate.status
            },
            'token': token
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """Resend OTP - Combined endpoint for admin, user, and affiliate"""
    serializer = ResendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get language from request (frontend can send it from localStorage for guest users)
        language = request.data.get('language') or request.data.get('preferredLanguage')
        if language and language not in ['en', 'ar']:
            language = None  # Invalid language, will default to 'en'
        
        result = AuthService.resend_otp_combined(
            serializer.validated_data['email'],
            serializer.validated_data['user_type'],
            language=language
        )
        
        return Response({
            'success': True,
            'message': 'OTP resent successfully',
            **result
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
