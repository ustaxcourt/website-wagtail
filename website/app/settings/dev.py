from .base import *  # noqa: F403
from .base import MIDDLEWARE  # noqa: F403
import os
from datetime import date

os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

DEBUG = False
BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"
ENVIRONMENT = "dev"

WAGTAIL_SITE_NAME = "A testing site for US Tax Court Web Development"

MIDDLEWARE = [
    "app.middleware.NoIndexMiddleware",
    "app.middleware.JSONExceptionMiddleware",
] + MIDDLEWARE

WAGTAIL_SITE_NAME = "A testing site for US Tax Court Web Development"

SITE_IS_LIVE = date.today() >= date(2025, 6, 1)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WAGTAILADMIN_NOTIFICATION_USE_HTML = False

WAGTAILADMIN_BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"
