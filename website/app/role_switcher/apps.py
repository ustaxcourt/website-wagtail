from django.apps import AppConfig


class RoleSwitcherConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.role_switcher"  # Make sure this matches your app's Python path
    verbose_name = "Role Switcher"

    def ready(self):
        # This import statement connects the signals defined in signals.py
        try:
            from . import signals  # noqa: F401
        except ImportError:
            # Handle cases where signals.py might not exist or other import issues
            pass
