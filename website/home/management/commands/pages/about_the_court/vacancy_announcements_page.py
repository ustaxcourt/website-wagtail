from wagtail.models import Page
from home.models import VacancyAnnouncementsPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)


class VacancyAnnouncementsPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        # Find the Employment page instead of home page
        try:
            employment_page = Page.objects.get(slug="employment")
        except Page.DoesNotExist:
            logger.info(
                "Error: Employment page does not exist. Please create it first."
            )
            return

        slug = "vacancy-announcements"
        title = "Vacancy Announcements"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        # Add as child of employment_page instead of home_page
        employment_page.add_child(
            instance=VacancyAnnouncementsPage(
                title=title,
                body="Current vacancy announcements for the United States Tax Court are listed below.",
                slug=slug,
                seo_title=title,
                search_description="Vacancy Announcements for the United States Tax Court",
            )
        )

        logger.info(f"Successfully created the '{title}' page.")
