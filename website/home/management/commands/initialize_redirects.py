from django.core.management.base import BaseCommand
from home.management.commands.redirects.redirect_initializer import RedirectInitializer


class Command(BaseCommand):
    help = "Create initial redirects if they don't already exist"

    def handle(self, *args, **options):
        initializer = RedirectInitializer(self.stdout)

        redirects = [
            {
                "old_path": "/vacancy_announcements",
                "new_path": "/employment/vacancy_announcements",
                "is_permanent": True,
            },
        ]

        for redirect in redirects:
            initializer.create_redirect(
                redirect["old_path"], redirect["new_path"], redirect["is_permanent"]
            )

        self.stdout.write(self.style.SUCCESS("All redirects have been initialized."))
