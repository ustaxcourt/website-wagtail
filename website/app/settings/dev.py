from .base import *  # noqa: F403
import os

os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

DEBUG = False
BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'
ENVIRONMENT = "dev"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = f"http://{ENVIRONMENT}-web.ustaxcourt.com"
