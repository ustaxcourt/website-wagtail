import os
from datetime import date

from .base import MIDDLEWARE

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False
BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"
ENVIRONMENT = "train"

MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE

ENABLE_LOCAL_LOGIN = True

# Disable password when new users are being created in admin console
WAGTAILUSERS_PASSWORD_REQUIRED = False
WAGTAILUSERS_PASSWORD_ENABLED = False

SITE_IS_LIVE = date.today() >= date(2999, 6, 1)
