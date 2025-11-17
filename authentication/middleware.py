"""
JWT Authentication Middleware
"""
from bson import ObjectId
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from authentication.services import JWTService
from authentication.models import Admin, User, Affiliate


class JWTAuthentication(BaseAuthentication):
    """JWT Authentication class"""
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        payload = JWTService.verify_token(token)
        
        if not payload:
            raise AuthenticationFailed('Invalid or expired token')
        
        user_type = payload.get('user_type')
        user_id = payload.get('user_id')
        
        # Convert string ID to ObjectId if needed
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
        except Exception:
            raise AuthenticationFailed('Invalid user ID format')
        
        if user_type == 'admin':
            user = Admin.objects(id=user_id).first()
        elif user_type == 'affiliate':
            user = Affiliate.objects(id=user_id).first()
        else:
            user = User.objects(id=user_id).first()
        
        if not user:
            raise AuthenticationFailed('User not found')
        
        return (user, token)

