from .base import *  # noqa: F403
from .base import LOGGING, MIDDLEWARE
import os


try:
    from .local import *  # noqa: F403

except ImportError:
    pass

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True
BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'
ENVIRONMENT = "sandbox"

LOGGING["root"]["handlers"] = ["console"]

MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE
