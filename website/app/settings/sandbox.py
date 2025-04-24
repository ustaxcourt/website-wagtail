from .base import *  # noqa: F403
from .base import LOGGING, MIDDLEWARE
import os

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

SECRET_KEY = os.getenv("SECRET_KEY")
CSRF_TRUSTED_ORIGINS = [f'https://{os.getenv("DOMAIN_NAME")}']
# TODO: verify if this is actually needed (read it was needed when using AWS ALB)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# TODO: verify if these are needed; I had to add / remove a lot of config before I got this all working, so these might not actually be needed
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

DEBUG = True
BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'
ENVIRONMENT = "sandbox"

LOGGING["root"]["handlers"] = ["console"]

MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE

