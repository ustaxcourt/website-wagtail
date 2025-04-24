from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check if the production environment is set up correctly"

    def handle(self, *args, **options):
        RAISE_ERROR = False
        # Check if DEBUG is False
        if settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is set to True."))
            RAISE_ERROR = True
        else:
            self.stdout.write(self.style.SUCCESS("DEBUG is set to False."))

        # Check if SECRET_KEY is set
        if not settings.SECRET_KEY:
            self.stdout.write(self.style.ERROR("SECRET_KEY is not set."))
            RAISE_ERROR = True
        else:
            self.stdout.write(self.style.SUCCESS("SECRET_KEY is set."))

        # Check if ALLOWED_HOSTS is set
        if not settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.ERROR("ALLOWED_HOSTS is not set."))
            RAISE_ERROR = True
        else:
            self.stdout.write(self.style.SUCCESS("ALLOWED_HOSTS is set."))

        if not settings.CSRF_COOKIE_SECURE:
            self.stdout.write(self.style.ERROR("CSRF_COOKIE_SECURE is not set."))
            RAISE_ERROR = True
        else:
            self.stdout.write(self.style.SUCCESS("CSRF_COOKIE_SECURE is set to True."))

        if not settings.SESSION_COOKIE_SECURE:
            self.stdout.write(self.style.ERROR("SESSION_COOKIE_SECURE is not set."))
            RAISE_ERROR = True
        else:
            self.stdout.write(
                self.style.SUCCESS("SESSION_COOKIE_SECURE is set to True.")
            )

        # Check if raising errors is enabled
        if RAISE_ERROR:
            self.stdout.write(self.style.ERROR("Production checks failed!"))
            raise RuntimeError("Production checks failed!")
        else:
            self.stdout.write(self.style.SUCCESS("All production checks passed!"))
