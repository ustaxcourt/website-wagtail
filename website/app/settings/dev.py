from .base import *  # noqa: F403
import os

# SECURITY WARNING: define the correct hosts in production!

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

# TODO: verify if this is actually needed (read it was needed when using AWS ALB)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# TODO: verify if these are needed; I had to add / remove a lot of config before I got this all working, so these might not actually be needed
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

DEBUG = False
BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'
ENVIRONMENT = "dev"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = f"http://{ENVIRONMENT}-web.ustaxcourt.com"
