from wagtail.models import Page
from home.models import EnhancedStandardPage, IconCategories, IndentStyle
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)


class CitationStyleManualPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "citation-and-style-manual"
        title = "Citation and Style Manual"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        # Load the PDF document
        document = self.load_document_from_documents_dir(
            None,
            "USTC_Citation_and_Style_Manual_modified_2024.09.pdf",
            "USTC Citation and Style Manual",
        )

        if not document:
            return

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Citation and Style Manual for the United States Tax Court",
                body=[
                    {
                        "type": "paragraph",
                        "value": (
                            "In January 2022, the Tax Court modified the format, citation, and style "
                            "used for all opinions and orders. The Citation and Style Manual was updated "
                            "September 2024 and is available below. Opinions and orders issued before 2022 "
                            "reflect the pre-2022 format and style."
                        ),
                    },
                    {
                        "type": "hr",
                        "value": True,
                    },
                    {
                        "type": "links",
                        "value": {
                            "class": IndentStyle.UNINDENTED,
                            "links": [
                                {
                                    "title": "USTC Citation and Style Manual",
                                    "icon": IconCategories.PDF,
                                    "document": document.id,
                                    "url": None,
                                },
                            ],
                        },
                    },
                ],
            )
        )

        logger.info(f"Successfully created the '{title}' page.")
