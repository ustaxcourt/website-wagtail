from django.core.management.base import BaseCommand
from django.conf import settings

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
from home.management.commands.pages.navigation import NavigationInitializer

from home.management.commands.snippets import (
    snippets_to_initialize,
    snippets_to_initialize_via_executescript,
)
from home.management.commands.redirects.redirect_initializer import RedirectInitializer

from home.management.commands.pages.documents import UnlistedFiles
from home.management.commands.pages.about_the_court import JudgesPageInitializer
from home.management.commands.pages.efiling_and_case_maintenance.dawson_page import (
    DawsonPageInitializer,
)
from home.management.commands.pages.card_tiles_test_page import (
    CardTilesTestPageInitializer,
)
from home.management.commands.snippets.call_to_action_box import (
    CallToActionBoxInitializer,
)

# Initialize home and footer first
home_page_initialize = [
    HomePageInitializer,
    FooterInitializer,
    RedirectPageInitializer,
]

# Ensure Home Page is initialized first
pages_to_initialize = home_page_initialize + (
    [CallToActionBoxInitializer]
    + about_the_court_pages_to_initialize
    + rules_and_guidance_pages_to_initialize
    + orders_and_opinions_pages_to_initialize
    + efiling_and_case_maintenance_pages_to_initialize
)

pages_to_update = [
    HomePageInitializer,
    JudgesPageInitializer,
    DawsonPageInitializer,
]


class Command(BaseCommand):
    help = "Create initial pages and form records if they don't already exist."

    def handle(self, *args, **options):
        # Initialize redirects first
        redirect_initializer = RedirectInitializer()
        redirect_initializer.create_redirect()

        self.stdout.write(self.style.SUCCESS("All redirects have been initialized."))

        # Continue with existing initialization
        if settings.SITE_IS_LIVE:
            self.stdout.write(
                "Skipping snippet creation. Snippets creation/recreation suppressed past site LIVE DATE."
            )
        else:
            self.stdout.write("Creating snippets...")
            for snippet_class in snippets_to_initialize:
                snippet_instance = snippet_class()
                snippet_instance.create()

        for snippet_class in snippets_to_initialize_via_executescript:
            snippet_instance = snippet_class()
            snippet_instance.run()

        for page_class in pages_to_initialize:
            page_instance = page_class()
            page_instance.create()

        self.stdout.write(self.style.SUCCESS("All pages have been initialized."))

        # Update pages
        for page_class in pages_to_update:
            page_instance = page_class()
            page_instance.update()

        self.stdout.write(self.style.SUCCESS("All pages have been updated."))

        # Initialize navigation last
        nav_initializer = NavigationInitializer()
        nav_initializer.create()
        self.stdout.write(self.style.SUCCESS("Navigation has been initialized."))

        # Initialize unlisted files
        unlisted_files_initializer = UnlistedFiles()
        unlisted_files_initializer.create()
        self.stdout.write(self.style.SUCCESS("Unlisted files have been initialized."))

        # Initialize card tiles test page (non-production only)
        if not settings.SITE_IS_LIVE:
            card_tiles_initializer = CardTilesTestPageInitializer()
            card_tiles_initializer.create()
            self.stdout.write(
                self.style.SUCCESS("Card Tiles test page has been initialized.")
            )
