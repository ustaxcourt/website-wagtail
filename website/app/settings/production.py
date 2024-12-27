import os
from .base import *  # noqa: F403

# TODO: I don't think we'd need this at all?
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# TODO: this should be configured based on the domain when we get one
ALLOWED_HOSTS = ["*"]
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True
