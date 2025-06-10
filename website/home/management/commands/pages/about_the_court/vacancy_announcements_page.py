from wagtail.models import Page
from home.models import VacancyAnnouncementsPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)

vacancy_announcements_docs = {
    "VA_Dep_Clerk_Admin_Svc_Final_20250424.pdf": "",
}


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

        for doc_name in vacancy_announcements_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            vacancy_announcements_docs[doc_name] = document

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
