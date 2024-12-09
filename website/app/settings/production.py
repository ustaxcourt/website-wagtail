import os
from .base import *  # noqa: F403

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ["*"]
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True
