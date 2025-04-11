from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE
import os
import subprocess

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-eygp9+*6&f+f)@u&qw#u4lue&%6j)95l!*1god6dw7i@yy13fn"

if INSTALLED_APPS:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

if MIDDLEWARE:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

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
