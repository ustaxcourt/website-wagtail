from django.core.management.base import BaseCommand

from home.management.commands.pages.about_the_court import (
    about_the_court_pages_to_initialize,
)

from home.management.commands.pages.rules_and_guidance import (
    rules_and_guidance_pages_to_initialize,
)

from home.management.commands.pages.efiling_and_case_maintenance import (
    efiling_and_case_maintenance_pages_to_initialize,
)

from home.management.commands.pages.orders_and_opinions import (
    orders_and_opinions_pages_to_initialize,
)

from home.management.commands.pages.home_page import HomePageInitializer
from home.management.commands.pages.redirect_page import RedirectPageInitializer
from home.management.commands.pages.footer import FooterInitializer

from home.management.commands.snippets import snippets_to_initialize

home_page_initialize = [
    HomePageInitializer,
    FooterInitializer,
    RedirectPageInitializer,
]

# Ensure Home Page is initialized first
pages_to_initialize = home_page_initialize + (
    about_the_court_pages_to_initialize
    + rules_and_guidance_pages_to_initialize
    + orders_and_opinions_pages_to_initialize
    + efiling_and_case_maintenance_pages_to_initialize
)

pages_to_update = [HomePageInitializer, FooterInitializer]


class Command(BaseCommand):
    help = "Create initial pages and form records if they don't already exist."

    def handle(self, *args, **options):
        for snippet_class in snippets_to_initialize:
            snippet_instance = snippet_class(self.stdout)
            snippet_instance.create()

        for page_class in pages_to_initialize:
            page_instance = page_class(self.stdout)
            page_instance.create()

        self.stdout.write(self.style.SUCCESS("All pages have been initialized."))

        for page_class in pages_to_update:
            page_instance = page_class(self.stdout)
            page_instance.update()

        self.stdout.write(self.style.SUCCESS("All pages have been updated."))
