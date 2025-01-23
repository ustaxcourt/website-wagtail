from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import CitationStyleManualPage
from wagtail.documents import get_document_model
from django.core.files import File
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories
import os


class CitationStyleManualPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "citation-style-manual"
        title = "Citation and Style Manual"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        # First create and upload the PDF document
        Document = get_document_model()
        pdf_path = "home/management/documents/citation_style_manual/USTC_Citation_and_Style_Manual_modified_2024.09.pdf"

        if not os.path.exists(pdf_path):
            self.logger.write(f"PDF file not found at {pdf_path}")
            return

        document = None
        with open(pdf_path, "rb") as pdf_file:
            document = Document(
                title="USTC Citation and Style Manual",
                file=File(pdf_file, name=os.path.basename(pdf_path)),
            )
            document.save()

        content_type = ContentType.objects.get_for_model(CitationStyleManualPage)

        body_text = (
            "In January 2022, the Tax Court modified the format, citation, and style "
            "used for all opinions and orders. The Citation and Style Manual was updated "
            "September 2024 and is available below. Opinions and orders issued before 2022 "
            "reflect the pre-2022 format and style."
        )

        new_page = home_page.add_child(
            instance=CitationStyleManualPage(
                title=title,
                body=body_text,
                document=document,
                slug=slug,
                seo_title=title,
                search_description="Citation and Style Manual for the United States Tax Court",
                content_type=content_type,
                show_in_menus=True,
            )
        )

        CitationStyleManualPage.objects.filter(id=new_page.id).update(
            menu_item_name="CITATION & STYLE MANUAL",
            navigation_category=NavigationCategories.ORDERS_AND_OPINIONS,
        )

        self.logger.write(f"Successfully created the '{title}' page.")
