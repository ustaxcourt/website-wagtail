from .base import *  # noqa: F403
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "django-insecure-eygp9+*6&f+f)@u&qw#u4lue&%6j)95l!*1god6dw7i@yy13fn"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

os.environ["DJANGO_SUPERUSER_PASSWORD"] = "ustcAdminPW!"

try:
    from .local import *  # noqa: F403

except ImportError:
    pass
