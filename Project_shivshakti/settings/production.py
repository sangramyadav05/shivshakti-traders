import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

SECRET_KEY = env('SECRET_KEY', env('DJANGO_SECRET_KEY', '')).strip()
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY must be set in production.')

# allowed_hosts_raw = env('ALLOWED_HOSTS', env('DJANGO_ALLOWED_HOSTS', '')).strip()

ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_raw.split(',') if host.strip()]

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS must be set in production.')

csrf_trusted_origins_raw = env('CSRF_TRUSTED_ORIGINS', env('DJANGO_CSRF_TRUSTED_ORIGINS', '')).strip()
if csrf_trusted_origins_raw:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted_origins_raw.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host not in {'localhost', '127.0.0.1'}]

CSRF_TRUSTED_ORIGINS = [
    os.environ.get("CSRF_TRUSTED_ORIGINS"),
]

DATABASE_URL = env('DATABASE_URL', '').strip()
if not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL must be set in production.')

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=env_int('POSTGRES_CONN_MAX_AGE', 600),
        ssl_require=True,
    )
}

STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env_int('SECURE_HSTS_SECONDS', 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'



INSTALLED_APPS += [
    "cloudinary",
    "cloudinary_storage",
]


import os

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"