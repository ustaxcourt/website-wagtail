from .base import *  # noqa: F403
from .base import MIDDLEWARE
import os
from datetime import date
import logging

logger = logging.getLogger(__name__)

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False
BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"
ENVIRONMENT = "train"

MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE

SITE_IS_LIVE = date.today() >= date(2999, 6, 1)

EMAIL_BACKEND = "django_ses.SESBackend"

logger.info(f"Email backend: {EMAIL_BACKEND}")
