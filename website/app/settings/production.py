import os
from .base import *  # noqa: F403

# TODO: I don't think we'd need this at all?
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# TODO: remove the *
# when I set this to [os.getenv("DOMAIN_NAME")], it seems to fail
# because ECS is doing a healthcheck on localhost:8000, but then django fails
# because that's not an allowed domain.  We may need to just add both the real domain and local host
ALLOWED_HOSTS = ["*"]
SECRET_KEY = os.getenv("SECRET_KEY")
CSRF_TRUSTED_ORIGINS = [f'https://{os.getenv("DOMAIN_NAME")}']
# TODO: verify if this is actually needed (read it was needed when using AWS ALB)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# TODO: verify if these are needed; I had to add / remove a lot of config before I got this all working, so these might not actually be needed
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

DEBUG = False

# Add this setting to store your GA tracking ID
GOOGLE_ANALYTICS_ID = "G-09HTDLXBMS"

ENVIRONMENT = "production"

BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'
