from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = "home"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import home.signals  # noqa
