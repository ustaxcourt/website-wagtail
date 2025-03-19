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

    def create(self):
        settings = NavigationMenu.objects.first()

        if settings:
            self.logger.write("- Navigation menu already exists.")
            return

        NavigationMenu.objects.create(
            menu_items=[
                (
                    "section",
                    {
                        "title": "ABOUT THE COURT",
                        "key": "ABOUT",
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
                                "page": self.get_page("trial-sessions"),
                                "external_url": "",
                            },
                            {
                                "title": "EMPLOYMENT",
                                "page": self.get_page("employment"),
                                "external_url": "",
                            },
                        ],
                    },
                ),
                (
                    "section",
                    {
                        "title": "RULES & GUIDANCE",
                        "key": "RULES",
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
                        "key": "ORDERS",
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
                        "key": "eFILING",
                        "sub_links": [
                            {
                                "title": "DAWSON (EFILING SYSTEM)",
                                "page": None,
                                "external_url": "https://dawson.ustaxcourt.gov/",
                            },
                            {
                                "title": "SEARCH (CASE, ORDER, OPINION, PRACTITIONER)",
                                "page": None,
                                "external_url": "https://dawson.ustaxcourt.gov/",
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
        )
        self.logger.write("Successfully created Navigation menu settings.")

    def update(self):
        settings = NavigationMenu.objects.first()
        if not settings:
            self.logger.write("- Can't find Navigation menu settings. STOPPING.")
            return

        self.logger.write(
            "- Navigation menu settings already exists. No updates needed."
        )
