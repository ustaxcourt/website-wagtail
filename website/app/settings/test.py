import os
from .base import *  # noqa: F403

# This test config was inspired by the Django-Styleguide-Example. Some of the
# settings were copied over from that project and may not be relevant yet.
# For more info see: https://github.com/HackSoftware/Django-Styleguide-Example
os.environ.setdefault("DEBUG_TOOLBAR_ENABLED", "False")

DEBUG = False

# Test-specific settings
SECRET_KEY = "test-secret-key-not-for-production"

# Use in-memory database for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Simplified password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable static file collection in tests
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
