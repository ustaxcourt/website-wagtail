import os
from .base import *  # noqa: F403

# TODO: I don't think we'd need this at all?
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ALLOWED_HOSTS = [os.getenv("DOMAIN_NAME")]
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False
