import os

# Preferred selector: DJANGO_ENV=production|development
env = os.getenv('DJANGO_ENV', '').strip().lower()
if env == 'production':
    from .production import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403
