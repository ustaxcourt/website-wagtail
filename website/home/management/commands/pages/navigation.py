from home.management.commands.pages.page_initializer import PageInitializer
from wagtail.models import Page
from home.models import NavigationMenu


class NavigationInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def get_page(self, slug):
        try:
            page = Page.objects.live().filter(slug=slug).first()
            if page:
                return page.specific
            self.logger.write(f"WARNING: Page with slug '{slug}' not found")
            return None
        except Page.DoesNotExist:
            self.logger.write(f"WARNING: Page with slug '{slug}' not found")
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
                            "external_url": "",
                        },
                        {
                            "title": "HISTORY",
                            "page": self.get_page("history"),
                            "external_url": "",
                        },
                        {
                            "title": "JUDGES",
                            "page": self.get_page("judges"),
                            "external_url": "",
                        },
                        {
                            "title": "TRIAL SESSIONS",
                            "page": None,
                            "external_url": "https://dawson.ustaxcourt.gov/trial-sessions",
                        },
                        {
                            "title": "EMPLOYMENT",
                            "page": self.get_page("employment"),
                            "external_url": "",
                        },
                        {
                            "title": "REPORTS & STATISTICS",
                            "page": self.get_page("reports-and-statistics"),
                            "external_url": "",
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
                            "external_url": "",
                        },
                        {
                            "title": "ADMINISTRATIVE ORDERS",
                            "page": self.get_page("administrative-orders"),
                            "external_url": "",
                        },
                        {
                            "title": "TAX COURT RULES",
                            "page": self.get_page("rules"),
                            "external_url": "",
                        },
                        {
                            "title": "GUIDANCE FOR PETITIONERS",
                            "page": self.get_page("petitioners"),
                            "external_url": "",
                        },
                        {
                            "title": "CLINICS & PRO BONO PROGRAMS",
                            "page": self.get_page("clinics"),
                            "external_url": "",
                        },
                        {
                            "title": "GUIDANCE FOR PRACTITIONERS",
                            "page": self.get_page("practitioners"),
                            "external_url": "",
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
                            "page": None,
                            "external_url": "https://dawson.ustaxcourt.gov/todays-opinions",
                        },
                        {
                            "title": "TODAY'S ORDERS",
                            "page": None,
                            "external_url": "https://dawson.ustaxcourt.gov/todays-orders",
                        },
                        {
                            "title": "SEARCH (CASE, ORDER, OPINION, PRACTITIONER)",
                            "page": None,
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                        {
                            "title": "CITATION & STYLE MANUAL",
                            "page": self.get_page("citation-and-style-manual"),
                            "external_url": "",
                        },
                        {
                            "title": "TRANSCRIPTS & COPIES",
                            "page": self.get_page("transcripts-and-copies"),
                            "external_url": "",
                        },
                        {
                            "title": "TAX COURT REPORTS: PAMPHLETS",
                            "page": self.get_page("pamphlets"),
                            "external_url": "",
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
                            "page": None,
                            "external_url": "https://dawson.ustaxcourt.gov/",
                        },
                        {
                            "title": "DAWSON (EFILING SYSTEM)",
                            "page": self.get_page("dawson"),
                            "external_url": "",
                        },
                        {
                            "title": "CASE RELATED FORMS",
                            "page": self.get_page("case-related-forms"),
                            "external_url": "",
                        },
                    ],
                },
            ),
        ]

    def create(self):
        # Delete existing navigation menu if it exists
        NavigationMenu.objects.all().delete()

        # Create a single navigation menu
        menu = NavigationMenu.objects.create(menu_items=self.get_default_menu_items())

        # Create an initial revision and publish it
        revision = menu.save_revision()
        revision.publish()

        self.logger.write("Successfully created Navigation menu.")
