from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import PressReleasePage

import logging

logger = logging.getLogger(__name__)


class PressReleasesPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "news-and-announcements"
        title = "News and Announcements"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        press_release_page = PressReleasePage(
            title=title,
            slug=slug,
            seo_title=title,
            search_description="News and Announcements",
            show_in_menus=True,
        )

        home_page.add_child(instance=press_release_page)
        press_release_page.save_revision().publish()
        logger.info(f"'{title}' page created and published.")
