import os

settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")

if settings_module:
    module = settings_module.split(".")[-1]
    if module == "production":
        from .production import *
    elif module == "development":
        from .development import *
else:
    from .development import *
