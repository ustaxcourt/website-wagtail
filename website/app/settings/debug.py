from .base import *  # noqa: F403
from .local import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE

if INSTALLED_APPS:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_COLLAPSED": True,
    }

if MIDDLEWARE:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
