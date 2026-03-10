from django.core.management.base import BaseCommand

from home.management.commands.pages.efiling_and_case_maintenance.LITC_page import (
    LITCPageInitializer,
)


class Command(BaseCommand):
    help = (
        "Create initial LITC Cities page and form records if they don't already exist."
    )

    def handle(self, *args, **options):
        page_instance = LITCPageInitializer()
        page_instance.create()

        self.stdout.write(
            self.style.SUCCESS("The LITC Cities page has been initialized.")
        )
