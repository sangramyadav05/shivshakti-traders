# Deployment Readiness

## 1) Production settings
Set these environment variables:

- DJANGO_ENV=production
- DJANGO_SETTINGS_MODULE=Project_shivshakti.settings
- DJANGO_SECRET_KEY=<strong-random-value>
- DJANGO_DEBUG=false
- DJANGO_ALLOWED_HOSTS=<domain>,www.<domain>
- DJANGO_CSRF_TRUSTED_ORIGINS=https://<domain>,https://www.<domain>

Security headers and CSP are enabled by default via settings + middleware.

## 2) Database (Render PostgreSQL)
Configure:

- DATABASE_URL=<render-postgres-internal-url>

## 3) Media storage on Render Free (Cloudinary)
Use Cloudinary (recommended for free tier):

- DJANGO_USE_CLOUDINARY=true
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET

Note: When Cloudinary is enabled, no persistent disk is required for product images.

## 4) Admin hardening
Set non-default paths:

- DJANGO_ADMIN_URL=<random-path>/
- DJANGO_ADMIN_LOGIN_URL=<custom-login>/

## 5) Email + reCAPTCHA
Set:

- DJANGO_ADMIN_NOTIFICATION_EMAIL
- DJANGO_DEFAULT_FROM_EMAIL
- DJANGO_EMAIL_BACKEND (SMTP backend in production)
- DJANGO_RECAPTCHA_ENABLED=true
- DJANGO_RECAPTCHA_SITE_KEY
- DJANGO_RECAPTCHA_SECRET_KEY

## 6) Login and enquiry throttling
Set:

- ENQUIRY_RATE_LIMIT_WINDOW_SECONDS
- ENQUIRY_RATE_LIMIT_MAX_REQUESTS
- LOGIN_RATE_LIMIT_WINDOW_SECONDS
- LOGIN_RATE_LIMIT_MAX_ATTEMPTS

## 7) Run deployment commands

- python manage.py migrate
- python manage.py collectstatic --noinput
- python manage.py check --deploy

## 8) WSGI/ASGI
Use:

- Project_shivshakti.wsgi:application
- Project_shivshakti.asgi:application
