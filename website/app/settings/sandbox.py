import os
from datetime import date

from .base import MIDDLEWARE

# Pull in any local overrides first (if present)
try:
    from .local import *  # noqa: F403
except ImportError:
    pass

# --- Core sandbox settings ---
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"
ENVIRONMENT = "sandbox"

# Prepend any sandbox-only middleware
MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE

# Sandbox site should not be treated as live
SITE_IS_LIVE = date.today() >= date(2999, 6, 1)

ENABLE_LOCAL_LOGIN = True
LOCAL_LOGIN_TOKEN = os.getenv("LOCAL_LOGIN_TOKEN", "")
CYPRESS_LOCAL_LOGIN_TOKEN = os.getenv("CYPRESS_LOCAL_LOGIN_TOKEN", "")

# settings.py
WAGTAILUSERS_PASSWORD_REQUIRED = False
WAGTAILUSERS_PASSWORD_ENABLED = False
