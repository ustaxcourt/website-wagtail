from django.core.management.base import BaseCommand
from home.management.commands.pages.efiling_and_case_maintenance import (
    efiling_and_case_maintenance_pages_to_update,
)
from home.management.commands.pages.about_the_court import (
    about_the_court_pages_to_update,
)
from home.management.commands.pages.home_page import HomePageInitializer
from home.management.commands.pages.footer import FooterInitializer
from home.management.commands.pages.navigation import NavigationInitializer

# Ensure Home Page is initialized first
pages_to_update = (
    about_the_court_pages_to_update
    + efiling_and_case_maintenance_pages_to_update
    + [FooterInitializer, NavigationInitializer]
)


class Command(BaseCommand):
    help = "Handle updates to pages and other content."

    def handle(self, *args, **options):
        for page_class in pages_to_update:
            page_instance = page_class()
            page_instance.run()

        home_initializer = HomePageInitializer()
        home_initializer.update_home_page()
        self.stdout.write(self.style.SUCCESS("All pages have been updated."))
