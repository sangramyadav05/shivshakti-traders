import os
from datetime import timedelta
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(name, default=None):
    return os.getenv(name, default)


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_int(name, default=0):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


INSECURE_SECRET_FALLBACK = 'django-insecure-change-me'
SECRET_KEY = env('DJANGO_SECRET_KEY', INSECURE_SECRET_FALLBACK)
DEBUG = env_bool('DJANGO_DEBUG', False)

if not DEBUG and SECRET_KEY == INSECURE_SECRET_FALLBACK:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set to a strong value in production.')

ALLOWED_HOSTS = [host.strip() for host in env('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in env('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt.token_blacklist',
    'core.apps.CoreConfig',
    'products.apps.ProductsConfig',
    'enquiries.apps.EnquiriesConfig',
    'accounts.apps.AccountsConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.ContentSecurityPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Project_shivshakti.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Project_shivshakti.wsgi.application'
ASGI_APPLICATION = 'Project_shivshakti.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SERVE_MEDIA = env_bool('DJANGO_SERVE_MEDIA', DEBUG)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Admin hardening
ADMIN_URL = env('DJANGO_ADMIN_URL', 'secure-control-panel/')
ADMIN_LOGIN_URL = env('DJANGO_ADMIN_LOGIN_URL', 'admin-login/')
ADMIN_LOGIN_RATELIMIT = env('DJANGO_ADMIN_LOGIN_RATELIMIT', '5/m')

# Enquiry protections
ENQUIRY_RATE_LIMIT_WINDOW_SECONDS = env_int('ENQUIRY_RATE_LIMIT_WINDOW_SECONDS', 300)
ENQUIRY_RATE_LIMIT_MAX_REQUESTS = env_int('ENQUIRY_RATE_LIMIT_MAX_REQUESTS', 5)
LOGIN_RATE_LIMIT_WINDOW_SECONDS = env_int('LOGIN_RATE_LIMIT_WINDOW_SECONDS', 300)
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = env_int('LOGIN_RATE_LIMIT_MAX_ATTEMPTS', 5)
RECAPTCHA_ENABLED = env_bool('DJANGO_RECAPTCHA_ENABLED', False)
RECAPTCHA_SITE_KEY = env('DJANGO_RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = env('DJANGO_RECAPTCHA_SECRET_KEY', '')
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', 'noreply@shivshaktitraders.com')
ADMIN_NOTIFICATION_EMAIL = env('DJANGO_ADMIN_NOTIFICATION_EMAIL', 'admin@shivshaktitraders.com')
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Caching (used for rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'shivshakti-default-cache',
    }
}

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Content Security Policy (CSP)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", 'https://cdn.tailwindcss.com', 'https://www.google.com', 'https://www.gstatic.com')
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", 'https://fonts.googleapis.com')
CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com', 'data:')
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_CONNECT_SRC = ("'self'", 'https://www.google.com')
CSP_FRAME_SRC = ('https://www.google.com', 'https://www.gstatic.com')
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)

# Logging
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'enquiries': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

ADMINS = [('Site Admin', ADMIN_NOTIFICATION_EMAIL)]

# DRF
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': env_int('API_PAGE_SIZE', 12),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('API_THROTTLE_ANON', '60/min'),
        'user': env('API_THROTTLE_USER', '120/min'),
        'products': env('API_THROTTLE_PRODUCTS', '120/min'),
        'enquiries': env('API_THROTTLE_ENQUIRIES', '30/min'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env_int('JWT_ACCESS_TOKEN_MINUTES', 15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env_int('JWT_REFRESH_TOKEN_DAYS', 7)),
    'ROTATE_REFRESH_TOKENS': env_bool('JWT_ROTATE_REFRESH_TOKENS', True),
    'BLACKLIST_AFTER_ROTATION': env_bool('JWT_BLACKLIST_AFTER_ROTATION', True),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SIGNING_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': False,
}

SPECTACULAR_SETTINGS = {
    'TITLE': env('API_TITLE', 'Shivshakti Traders API'),
    'VERSION': env('API_VERSION', 'v1'),
    'DESCRIPTION': env(
        'API_DESCRIPTION',
        'REST API for Shivshakti Traders products and enquiries. '
        'Use JWT Bearer token for protected endpoints.',
    ),
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'SECURITY_SCHEMES': {
        'BearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    },
}
