from .base import *  # noqa: F403
from .base import LOGGING  # noqa: F403
import os
import subprocess
from datetime import date

from .base import LOGGING  # noqa: F403

# ------------------------------------------------------------
# Local/dev toggles
# ------------------------------------------------------------
os.environ.setdefault("DEBUG_TOOLBAR_ENABLED", "False")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-eygp9+*6&f+f)@u&qw#u4lue&%6j)95l!*1god6dw7i@yy13fn"

# Convenience for createsuperuser in local dev
os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")

ENVIRONMENT = "local"

if not os.getenv("GITHUB_SHA"):
    GITHUB_SHA = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        or "development"
    )

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = "http://localhost:8000"
BASE_URL = "http://localhost:8000"

# ------------------------------------------------------------
# Enable the hidden local (emergency) login page in dev
# Visit: http://127.0.0.1:8000/admin/local-login/
# If you want to gate it with a token, set LOCAL_LOGIN_TOKEN to a non-empty value
# and pass ?token=YOUR_VALUE on the URL.
# ------------------------------------------------------------
ENABLE_LOCAL_LOGIN = True
LOCAL_LOGIN_TOKEN = ""
CYPRESS_LOCAL_LOGIN_TOKEN = ""

WAGTAILUSERS_PASSWORD_REQUIRED = False
WAGTAILUSERS_PASSWORD_ENABLED = False


# ------------------------------------------------------------
# Logging: use the simple (human-readable) logger locally
# ------------------------------------------------------------
LOGGING["root"]["handlers"] = ["simple"]
LOGGING["loggers"]["django"]["handlers"] = ["simple"]
LOGGING["loggers"]["wagtail"]["handlers"] = ["simple"]
LOGGING["loggers"]["home"]["handlers"] = ["simple"]
LOGGING["loggers"]["home"]["level"] = "DEBUG"
LOGGING["loggers"]["home.management.commands"]["level"] = "DEBUG"

# Local/dev site should not be treated as live
SITE_IS_LIVE = date.today() >= date(2999, 6, 1)
