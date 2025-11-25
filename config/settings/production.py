from .base import *
import os
import dj_database_url
from pathlib import Path # Required for defining BASE_DIR paths

# -------------------------------------------------------------
# PATH CONFIGURATION (Ensure BASE_DIR is correctly defined)
# -------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# -------------------------------------------------------------
# STATIC FILES CONFIGURATION (REQUIRED FOR DEPLOYMENT)
# -------------------------------------------------------------

# Mandatory setting for 'collectstatic' to know where to dump Admin/DRF assets
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# The public URL prefix for static files
STATIC_URL = '/static/'

# WhiteNoise Configuration for serving static files efficiently
# NOTE: This assumes MIDDLEWARE is a list imported from base.py
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Use WhiteNoise's optimized storage backend
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# -------------------------------------------------------------
# DATABASE AND CACHE CONFIGURATION
# -------------------------------------------------------------

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Remove CORS settings
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'corsheaders']
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'corsheaders.middleware.CorsMiddleware']