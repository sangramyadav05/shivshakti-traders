from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must be set in production.')

if not ALLOWED_ADMIN_IPS:
    raise ImproperlyConfigured('DJANGO_ALLOWED_ADMIN_IPS must be set in production.')

DATABASE_URL = env('DATABASE_URL', '').strip()
if not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL must be set in production.')

if not REDIS_URL:
    raise ImproperlyConfigured('REDIS_URL must be set in production for Celery broker.')

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=env_int('POSTGRES_CONN_MAX_AGE', 60),
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

# Render media configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(env('DJANGO_MEDIA_ROOT', '/var/data/media'))
SERVE_MEDIA = env_bool('DJANGO_SERVE_MEDIA', True)

# Sentry (production-only, DSN-gated)
SENTRY_DSN = env('SENTRY_DSN', '').strip()
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=env('DJANGO_ENV', 'production'),
        traces_sample_rate=float(env('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        send_default_pii=False,
    )
