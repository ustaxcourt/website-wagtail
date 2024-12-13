import os
# This test config was inspired by the Django-Styleguide-Example. Some of the 
# settings were copied over from that project and may not be relevant yet.
# For more info see: https://github.com/HackSoftware/Django-Styleguide-Example
os.environ.setdefault("DEBUG_TOOLBAR_ENABLED", "False")

from .base import *  # noqa: F403


DEBUG = False
