import os
from .base import *  # noqa: F403
from .base import MIDDLEWARE  # noqa: F403
from datetime import date

DEBUG = False

# Add this setting to store your GA tracking ID
GOOGLE_ANALYTICS_ID = "G-09HTDLXBMS"

ENVIRONMENT = "production"

BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"

WAGTAIL_SITE_NAME = "Official Site of the United States Tax Court."

MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE

SITE_IS_LIVE = date.today() >= date(2025, 6, 1)

EMAIL_BACKEND = "django_ses.SESBackend"

WAGTAILADMIN_NOTIFICATION_USE_HTML = True

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "search.backends.custompostgres",
    }
}

LINK_CHECK_ENABLED = True
