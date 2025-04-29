from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, IconCategories
import logging

logger = logging.getLogger(__name__)


class EmploymentPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "employment"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Employment"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description="Employment",
                body=[
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Vacancy Announcements",
                                    "icon": IconCategories.CHEVRON_RIGHT,
                                    "document": None,
                                    "url": "/employment/vacancy-announcements",
                                },
                                {
                                    "title": "Internship Programs",
                                    "icon": IconCategories.CHEVRON_RIGHT,
                                    "document": None,
                                    "url": "/employment/internship-programs",
                                },
                                {
                                    "title": "Law Clerk Program",
                                    "icon": IconCategories.CHEVRON_RIGHT,
                                    "document": None,
                                    "url": "/employment/law-clerk-program",
                                },
                            ],
                        },
                    },
                ],
            )
        )

        logger.info(f"Created the '{title}' page.")
