from django.core.exceptions import ImproperlyConfigured
from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', 'shivshakti'),
        'USER': env('POSTGRES_USER', 'shivshakti_user'),
        'PASSWORD': env('POSTGRES_PASSWORD', ''),
        'HOST': env('POSTGRES_HOST', 'localhost'),
        'PORT': env('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': env_int('POSTGRES_CONN_MAX_AGE', 60),
        'OPTIONS': {
            'sslmode': env('POSTGRES_SSLMODE', 'require'),
        },
    }
}

if DATABASES['default']['OPTIONS'].get('sslmode') != 'require':
    raise ImproperlyConfigured('POSTGRES_SSLMODE must be set to "require" in production.')

SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env_int('DJANGO_SECURE_HSTS_SECONDS', 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
