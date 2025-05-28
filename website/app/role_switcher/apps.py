from django.apps import AppConfig

class RoleSwitcherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Adjust the name to match how your app is registered in INSTALLED_APPS
    # e.g., 'app.role_switcher' or just 'role_switcher'
    name = 'app.role_switcher' # Make sure this matches your app's Python path
    verbose_name = "Role Switcher"

    def ready(self):
        # This import statement connects the signals defined in signals.py
        try:
            from . import signals # Or from . import signals
        except ImportError:
            # Handle cases where signals.py might not exist or other import issues
            pass
