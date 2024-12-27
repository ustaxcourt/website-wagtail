import os
from .base import *  # noqa: F403

# TODO: I don't think we'd need this at all?
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ALLOWED_HOSTS = ["*"]  # temp fix [os.getenv("DOMAIN_NAME")]
SECRET_KEY = os.getenv("SECRET_KEY")
CSRF_TRUSTED_ORIGINS = [f'https://{os.getenv("DOMAIN_NAME")}']
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

print(os.environ)

DEBUG = False
