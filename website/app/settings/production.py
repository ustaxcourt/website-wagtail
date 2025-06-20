import os
from .base import *  # noqa: F403
from datetime import date

DEBUG = False

# Add this setting to store your GA tracking ID
GOOGLE_ANALYTICS_ID = "G-09HTDLXBMS"

ENVIRONMENT = "production"

BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = "http://ustaxcourt.com"
SITE_IS_LIVE = date.today() >= date(2025, 6, 1)
