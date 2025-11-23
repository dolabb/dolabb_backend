"""
Django settings for dolabb_backend project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import mongoengine

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'authentication',
    'admin_dashboard',
    'products',
    'chat',
    'payments',
    'affiliates',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dolabb_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dolabb_backend.wsgi.application'
ASGI_APPLICATION = 'dolabb_backend.asgi.application'

# MongoDB Configuration
MONGODB_CONNECTION_STRING = os.getenv(
    'MONGODB_CONNECTION_STRING',
    'mongodb+srv://dolabb_admin:Farad2025%24@cluster0.0imvu6l.mongodb.net/dolabb_db?retryWrites=true&w=majority'
)

# Connect to MongoDB using mongoengine
mongoengine.connect(
    host=MONGODB_CONNECTION_STRING,
    alias='default'
)

# Database - Using MongoDB with mongoengine, Django DB config not needed
# But Django requires a DATABASES setting, so we use a dummy SQLite config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# VPS Storage Configuration (for GoDaddy VPS)
VPS_ENABLED = os.getenv('VPS_ENABLED', 'False').lower() == 'true'
VPS_HOST = os.getenv('VPS_HOST', '')
VPS_PORT = int(os.getenv('VPS_PORT', '22'))
VPS_USERNAME = os.getenv('VPS_USERNAME', '')
VPS_PASSWORD = os.getenv('VPS_PASSWORD', '')
VPS_KEY_PATH = os.getenv('VPS_KEY_PATH', '')
VPS_BASE_PATH = os.getenv('VPS_BASE_PATH', '/home/dolabbadmin/public_html/media')  # Default for GoDaddy VPS
VPS_BASE_URL = os.getenv('VPS_BASE_URL', '')  # e.g., 'https://www.dolabb.com/media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.middleware.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('PAGE_DEFAULT_LIMIT', 10)),
    'EXCEPTION_HANDLER': 'dolabb_backend.utils.custom_exception_handler',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

CORS_ALLOW_CREDENTIALS = True

# JWT Configuration
JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'your_jwt_secret_here')
JWT_EXPIRES_IN = os.getenv('JWT_EXPIRES_IN', '1d')
OTP_EXPIRY_SECONDS = int(os.getenv('OTP_EXPIRY_SECONDS', 300))

# Resend Email Configuration
# Note: In production, these MUST be set via environment variables
# Default values are for local development only
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
RESEND_FROM_EMAIL = os.getenv('RESEND_FROM_EMAIL', '')

# Moyasar Payment Configuration
MOYASAR_PUBLIC_KEY = os.getenv('MOYASAR_PUBLIC_KEY', '')
MOYASAR_SECRET_KEY = os.getenv('MOYASAR_SECRET_KEY', '')
MOYASAR_API_URL = 'https://api.moyasar.com/v1/payments'

# Channels Configuration (WebSockets)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

