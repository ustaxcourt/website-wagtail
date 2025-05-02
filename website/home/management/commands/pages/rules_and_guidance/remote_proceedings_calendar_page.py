from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)


class RemoteProceedingsCalendarPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "remote-proceedings"
        title = "Public Access to Remote Proceedings"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Links to remote proceedings will be displayed here and become active only when the proceeding is called to order.",
                body=[
                    {
                        "type": "paragraph",
                        "value": "Links to remote proceedings will be displayed here and become active only when the proceeding is called to order, which may be later than the time listed.",
                    },
                    {
                        "type": "iframe",
                        "value": {
                            "src": "https://outlook.office365.com/owa/calendar/eb75c2498efd4022ba69a506381bbb5e@ustaxcourt.gov/dbcf56e19a284716b9ad076bd7b10b7417016961165202484748/calendar.html",
                            "width": "1440",
                            "height": "360",
                            "class": "offsite",
                            "loading": "eager",
                            "data_delay": "2000",
                            "name": "Remote Proceedings",
                            "title": "Remote Proceedings",
                        },
                    },
                ],
            )
        )

        logger.info(f"Successfully created the '{title}' page.")
