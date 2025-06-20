from django.conf import settings
from home.management.commands.pages.page_initializer import PageInitializer
from wagtail.models import Page
from home.models import NavigationMenu
import logging

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
                    "title": "ABOUT THE COURT",
                    "sub_links": [
                        {
                            "title": "MISSION",
                            "page": self.get_page("mission"),
                        },
                        {
                            "title": "HISTORY",
                            "page": self.get_page("history"),
                        },
                        {
                            "title": "REPORTS & STATISTICS",
                            "page": self.get_page("reports-and-statistics"),
                        },
                        {
                            "title": "JUDGES",
                            "page": self.get_page("judges"),
                        },
                        {
                            "title": "DIRECTORY",
                            "page": self.get_page("directory"),
                        },
                        {
                            "title": "TRIAL SESSIONS",
                            "external_url": "https://dawson.ustaxcourt.gov/trial-sessions",
                        },
                        {
                            "title": "FEES & CHARGES",
                            "page": self.get_page("fees-and-charges"),
                        },
                        {
                            "title": "EMPLOYMENT",
                            "page": self.get_page("employment"),
                        },
                        {
                            "title": "PRESS RELEASES & NEWS",
                            "page": self.get_page("press-releases"),
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
                            "title": "REMOTE PROCEEDINGS",
                            "page": self.get_page("zoomgov"),
                        },
                        {
                            "title": "ADMINISTRATIVE ORDERS",
                            "page": self.get_page("administrative-orders"),
                        },
                        {
                            "title": "TAX COURT RULES",
                            "page": self.get_page("rules"),
                        },
                        {
                            "title": "GUIDANCE FOR PETITIONERS",
                            "page": self.get_page("petitioners"),
                        },
                        {
                            "title": "CLINICS & PRO BONO PROGRAMS",
                            "page": self.get_page("clinics"),
                        },
                        {
                            "title": "GUIDANCE FOR PRACTITIONERS",
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
                            "title": "TODAY'S OPINIONS",
                            "external_url": "https://dawson.ustaxcourt.gov/todays-opinions",
                        },
                        {
                            "title": "TODAY'S ORDERS",
                            "external_url": "https://dawson.ustaxcourt.gov/todays-orders",
                        },
                        {
                            "title": "SEARCH (CASE, ORDER, OPINION, PRACTITIONER)",
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                        {
                            "title": "CITATION & STYLE MANUAL",
                            "page": self.get_page("citation-and-style-manual"),
                        },
                        {
                            "title": "TRANSCRIPTS & COPIES",
                            "page": self.get_page("transcripts-and-copies"),
                        },
                        {
                            "title": "TAX COURT REPORTS: PAMPHLETS",
                            "page": self.get_page("pamphlets"),
                        },
                    ],
                },
            ),
            (
                "section",
                {
                    "title": "EFILING & CASE MAINTENANCE",
                    "sub_links": [
                        {
                            "title": "SEARCH (CASE, ORDER, OPINION, PRACTITIONER)",
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                        {
                            "title": "DAWSON (EFILING SYSTEM)",
                            "page": self.get_page("dawson"),
                        },
                        {
                            "title": "CASE RELATED FORMS",
                            "page": self.get_page("case-related-forms"),
                        },
                    ],
                },
            ),
            (
                "section",
                {
                    "title": "GIVE FEEDBACK",
                    "external_url": "https://forms.office.com/r/45R5iAguPG",
                    "sub_links": [],
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
