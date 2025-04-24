from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


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

        # Check if the superuser exists
        User = get_user_model()
        super_users = User.objects.filter(is_superuser=True)
        super_users_count = super_users.count()
        if super_users_count == 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Exactly one superuser found: {super_users[0].username}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"{super_users_count} superusers found. Exactly one expected."
                )
            )
            RAISE_ERROR = True

        # Check if no other user have password login
        for u in User.objects.filter(is_superuser=False):
            if u.has_usable_password():
                RAISE_ERROR = True
                self.stdout.write(
                    self.style.ERROR(
                        f"User {u.username} has a password login configured."
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("No other generic user/password login.")
            )

        # Check if raising errors is enabled
        if RAISE_ERROR:
            self.stdout.write(self.style.ERROR("Production checks failed!"))
            raise RuntimeError("Production checks failed!")
        else:
            self.stdout.write(self.style.SUCCESS("All production checks passed!"))
