"""
Authentication serializers
"""
from rest_framework import serializers
from authentication.models import Admin, User, Affiliate


class AdminSignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    profile_image_url = serializers.URLField(required=False, allow_blank=True)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AdminResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)


class UserSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    country_code = serializers.CharField(max_length=10, required=False)
    dial_code = serializers.CharField(max_length=10, required=False)
    profile_image_url = serializers.URLField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=['buyer', 'seller'], default='buyer', required=False)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate that either username or email is provided"""
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        
        if not username and not email:
            raise serializers.ValidationError("Either username or email is required")
        
        if username and email:
            raise serializers.ValidationError("Please provide either username or email, not both")
        
        return data


class UserForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)


class AffiliateSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    country_code = serializers.CharField(max_length=10)
    bank_name = serializers.CharField(max_length=200)
    account_number = serializers.CharField(max_length=100)
    iban = serializers.CharField(max_length=100, required=False, allow_blank=True)
    account_holder_name = serializers.CharField(max_length=200, required=False)
    profile_image_url = serializers.URLField(required=False, allow_blank=True)


class AffiliateLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AffiliateForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AffiliateResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    user_type = serializers.ChoiceField(choices=['admin', 'user', 'affiliate'])


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    user_type = serializers.ChoiceField(choices=['admin', 'user', 'affiliate'])


class UserProfileSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    full_name = serializers.CharField()
    profile_image = serializers.CharField()
    bio = serializers.CharField()
    location = serializers.CharField()
    shipping_address = serializers.CharField()
    zip_code = serializers.CharField()
    house_number = serializers.CharField()
    joined_date = serializers.DateTimeField()
    role = serializers.CharField()

