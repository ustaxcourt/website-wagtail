from .base import *  # noqa: F403
from .base import LOGGING  # noqa: F403
import os
import subprocess

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-eygp9+*6&f+f)@u&qw#u4lue&%6j)95l!*1god6dw7i@yy13fn"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")
ENVIRONMENT = "local"

if not os.getenv("GITHUB_SHA"):
    GITHUB_SHA = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        or "development"
    )

# Use the simple logger when running local
LOGGING["root"]["handlers"] = ["simple"]
LOGGING["loggers"]["django"]["handlers"] = ["simple"]
LOGGING["loggers"]["wagtail"]["handlers"] = ["simple"]
LOGGING["loggers"]["home"]["handlers"] = ["simple"]
LOGGING["loggers"]["home"]["level"] = "DEBUG"
LOGGING["loggers"]["home.management.commands"]["level"] = "DEBUG"
