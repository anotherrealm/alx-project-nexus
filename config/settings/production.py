import os
import dj_database_url
from .base import *


# ----------------------------------------
# 1. Core Settings
# ----------------------------------------

DEBUG = False

# Use the environment variable ALOWED_HOSTS you set on Railway
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Secret Key is mandatory and must be set on Railway
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("SECRET_KEY not found in environment variables.")

# ----------------------------------------
# 2. Database Configuration (Updated)
# ----------------------------------------

# Use dj_database_url to parse the single DATABASE_URL provided by Railway
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600  # Persistent connections
        )
    }
else:
    # Fallback to individual variables if DATABASE_URL is not set
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }


# ----------------------------------------
# 3. Static Files (Updated)
# ----------------------------------------

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
# CRITICAL: This configures WhiteNoise to handle static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ----------------------------------------
# 4. Middleware (CRITICAL ADDITION)
# ----------------------------------------

# Add WhiteNoise to the start of the MIDDLEWARE list
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')


# ----------------------------------------
# 5. Security Settings (Original code is good)
# ----------------------------------------

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Email configuration for production (Original code is good)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')