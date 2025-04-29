from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)


class MissionPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "mission"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Mission Statement"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": """The mission of the United States Tax Court is to provide a national forum for the expeditious resolution of disputes between taxpayers and the Internal Revenue Service; for careful consideration of the merits of each case; and to ensure a uniform interpretation of the Internal Revenue Code. The Court is committed to providing taxpayers, most of whom are self-represented, with a reasonable opportunity to appear before the Court, with as little inconvenience and expense as is practicable. The Court is also committed to providing an accessible judicial forum with simplified procedures for disputes involving $50,000 or less.
<p>If you are unfamiliar with the Tax Court or would like information about starting a case or representing yourself before the Court, please visit <a href="/petitioners" title="Guidance for Petitioners" >Guidance for Petitioners</a>.</p>""",
                    },
                ],
            )
        )

        logger.info(f"Created the '{title}' page.")
