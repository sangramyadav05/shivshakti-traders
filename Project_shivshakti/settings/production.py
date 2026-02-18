from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .base import *
from decouple import config
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default=config('ALLOWED_HOSTS', default='')
).split(',')
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must be set in production.')

DATABASE_URL = config('DATABASE_URL', default='').strip()
if not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL must be set in production.')

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=60,
        ssl_require=True
    )
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Render media configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(config('DJANGO_MEDIA_ROOT', default='/var/data/media'))
SERVE_MEDIA = config('DJANGO_SERVE_MEDIA', default=True, cast=bool)
