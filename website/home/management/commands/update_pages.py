from django.core.management.base import BaseCommand

from home.management.commands.pages.about_the_court import (
    about_the_court_pages_to_update,
)

# Ensure Home Page is initialized first
pages_to_update = about_the_court_pages_to_update


class Command(BaseCommand):
    help = "Handle updates to pages and other content."

    def handle(self, *args, **options):
        # Update pages
        for page_class in pages_to_update:
            page_instance = page_class()
            page_instance.run()

        self.stdout.write(self.style.SUCCESS("All pages have been updated."))
