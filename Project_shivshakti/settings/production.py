from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .base import *
from decouple import config
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default=config('ALLOWED_HOSTS', default='*')
).split(',')

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=60,
        ssl_require=True,
    )
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if USE_CLOUDINARY:
    required = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing = [name for name in required if not config(name, default='').strip()]
    if missing:
        raise ImproperlyConfigured(f'Missing Cloudinary environment variables: {", ".join(missing)}')
    SERVE_MEDIA = False
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = Path(config('DJANGO_MEDIA_ROOT', default='/var/data/media'))
    SERVE_MEDIA = config('DJANGO_SERVE_MEDIA', default=True, cast=bool)
