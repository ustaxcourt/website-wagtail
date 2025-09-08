from .base import *  # noqa: F403
from .base import MIDDLEWARE
import os
from datetime import date
import importlib

# Pull in any local overrides first (if present)
try:
    from .local import *  # noqa: F403
except ImportError:
    pass

# --- Core sandbox settings ---
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
BASE_URL = f"https://{os.getenv('DOMAIN_NAME')}"
ENVIRONMENT = "sandbox"

# Prepend any sandbox-only middleware
MIDDLEWARE = ["app.middleware.JSONExceptionMiddleware"] + MIDDLEWARE

# Sandbox site should not be treated as live
SITE_IS_LIVE = date.today() >= date(2999, 6, 1)

ENABLE_LOCAL_LOGIN = True
LOCAL_LOGIN_TOKEN = os.getenv(
    "LOCAL_LOGIN_TOKEN", ""
)  # set to non-empty to require ?token=...
CYPRESS_LOCAL_LOGIN_TOKEN = os.getenv("CYPRESS_LOCAL_LOGIN_TOKEN", "")

# --- Enforce password-less Wagtail user forms in sandbox ---
# Hides password fields on Add/Edit User; new users get unusable passwords (SSO-only)
WAGTAIL_USER_CREATION_FORM = "app.role_switcher.forms.SSOOnlyUserCreationForm"
WAGTAIL_USER_EDIT_FORM = "app.role_switcher.forms.SSOOnlyUserEditForm"

# --- Ensure hooks are loaded (especially if import order differs) ---
# Wagtail auto-loads modules named 'wagtail_hooks.py' in installed apps.
# If your hooks live there, this import is redundant but harmless.
for module_name in (
    "app.role_switcher.wagtail_hooks",
    "home.wagtail_hooks",
):
    try:
        importlib.import_module(module_name)
    except Exception:
        # Safe to ignore if a module doesn't exist in this project
        pass
