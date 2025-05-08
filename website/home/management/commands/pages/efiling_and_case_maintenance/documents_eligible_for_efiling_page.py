from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import CSVUploadPage
import logging

logger = logging.getLogger(__name__)


class DocumentsEligibleEfilingPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "documents-eligible-for-efiling"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "What Documents May be eFiled?"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        csv_document = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="efiling_eligible_documents_list.csv",
            title="efiling_eligible_documents_list.csv",
        )

        new_page = home_page.add_child(
            instance=CSVUploadPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                csv_file=csv_document.file,
            )
        )
        logger.info(f"Successfully created the '{title}' page.")
        new_page.save()
