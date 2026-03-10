from django.conf import settings
from home.management.commands.pages.page_initializer import PageInitializer
from wagtail.models import Page
from home.models import NavigationMenu
import logging

from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class NavigationInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def get_page(self, slug):
        try:
            page = Page.objects.live().filter(slug=slug).first()
            if page:
                return page.specific
            logger.info(f"WARNING: Page with slug '{slug}' not found")
            return None
        except Page.DoesNotExist:
            logger.info(f"WARNING: Page with slug '{slug}' not found")
            return None

    def get_default_menu_items(self):
        return [
            (
                "section",
                {
                    "title": "COURT INFORMATION",
                    "sub_links": [
                        {
                            "title": "Mission",
                            "page": self.get_page("mission"),
                        },
                        {
                            "title": "History",
                            "page": self.get_page("history"),
                        },
                        {
                            "title": "Reports & Statistics",
                            "page": self.get_page("reports-and-statistics"),
                        },
                        {
                            "title": "Judges",
                            "page": self.get_page("judges"),
                        },
                        {
                            "title": "Directory",
                            "page": self.get_page("directory"),
                        },
                        {
                            "title": "Trial Sessions",
                            "external_url": "https://dawson.ustaxcourt.gov/trial-sessions",
                        },
                        {
                            "title": "Fees & Charges",
                            "page": self.get_page("fees-and-charges"),
                        },
                        {
                            "title": "Employment",
                            "page": self.get_page("employment"),
                        },
                        {
                            "title": "News and Announcements",
                            "page": self.get_page("news-and-announcements"),
                        },
                    ],
                },
            ),
            (
                "section",
                {
                    "title": "RULES & GUIDANCE",
                    "sub_links": [
                        {
                            "title": "Remote Proceedings",
                            "page": self.get_page("zoomgov"),
                        },
                        {
                            "title": "Administrative Orders",
                            "page": self.get_page("administrative-orders"),
                        },
                        {
                            "title": "Tax Court Rules",
                            "page": self.get_page("rules"),
                        },
                        {
                            "title": "Guidance For Petitioners",
                            "page": self.get_page("petitioners"),
                        },
                        {
                            "title": "Clinics & Pro Bono Programs",
                            "page": self.get_page("clinics"),
                        },
                        {
                            "title": "Guidance For Practitioners",
                            "page": self.get_page("practitioners"),
                        },
                    ],
                },
            ),
            (
                "section",
                {
                    "title": "ORDERS & OPINIONS",
                    "sub_links": [
                        {
                            "title": "Today's Opinions",
                            "external_url": "https://dawson.ustaxcourt.gov/todays-opinions",
                        },
                        {
                            "title": "Today's Orders",
                            "external_url": "https://dawson.ustaxcourt.gov/todays-orders",
                        },
                        {
                            "title": "Search (Case, Order, Opinion, Practitioner)",
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                        {
                            "title": "Citation & Style Manual",
                            "page": self.get_page("citation-and-style-manual"),
                        },
                        {
                            "title": "Transcripts & Copies",
                            "page": self.get_page("transcripts-and-copies"),
                        },
                        {
                            "title": "Tax Court Reports: Pamphlets",
                            "page": self.get_page("pamphlets"),
                        },
                    ],
                },
            ),
            (
                "section",
                {
                    "title": "TRIALS & CASE MANAGEMENT",
                    "sub_links": [
                        {
                            "title": "Search (Case, Order, Opinion, Practitioner)",
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                        {
                            "title": "DAWSON (Efiling System)",
                            "page": self.get_page("dawson"),
                        },
                        {
                            "title": "Case Related Forms",
                            "page": self.get_page("case-related-forms"),
                        },
                    ],
                },
            ),
            (
                "section",
                {
                    "title": "RESOURCES",
                    "sub_links": [
                        {
                            "title": "DAWSON FAQ's",
                            "page": self.get_page("dawson-faqs-searches-public-access"),
                        },
                        {
                            "title": "DAWSON User Guides",
                            "page": self.get_page("dawson-user-guides"),
                        },
                        {
                            "title": "Tax Court Forms",
                            "page": self.get_page("case-related-forms"),
                        },
                        {
                            "title": "Tax Court Definitions",
                            "page": self.get_page("definitions"),
                        },
                        {
                            "title": "Look Up a Practitioner",
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                    ],
                },
            ),
        ]

    def create(self):
        # Delete existing navigation menu if it exists
        if settings.SITE_IS_LIVE:
            logger.info(
                "Skipping Navigation creation. Navigation menu creation/recreation suppressed past site LIVE DATE."
            )
            return
        else:
            logger.info("Creating Navigation menu...")
            NavigationMenu.objects.all().delete()

        # Create a single navigation menu
        menu = NavigationMenu.objects.create(menu_items=self.get_default_menu_items())

        # Create an initial revision and publish it
        revision = menu.save_revision()
        revision.publish()

        logger.info("Successfully created Navigation menu.")

    def update(self):
        logger.info("Updating Navigation menu...")
        NavigationMenu.objects.all().delete()
        # Create a single navigation menu
        menu = NavigationMenu.objects.create(menu_items=self.get_default_menu_items())

        # Create a new revision and publish it
        revision = menu.save_revision()
        revision.publish()
        logger.info("Successfully created Navigation menu.")

    def run(self):
        """Update the navigation menu as an execution script"""
        command_name = "Navigation menu update for homepage redesign"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.update()
            execution_log_text = "Navigation menu updated for homepage redesign"
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
