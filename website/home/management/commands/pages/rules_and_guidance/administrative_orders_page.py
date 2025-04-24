from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page
from home.models import AdministrativeOrdersPage, PDFs
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)

# Example PDF data
ADMIN_ORDERS_DATA = [
    {
        "title": "Administrative Order 2024-01 - Protocols for Entry into the Washington, D.C. Courthouse and In-Person Court Proceedings in Other Locations",
        "name": "Administrative_Order_2024-01.pdf",
    },
    {
        "title": "Administrative Order 2023-02 - Expanding Remote Electronic Access to Certain Court Documents",
        "name": "Administrative_Order_2023-02.pdf",
    },
    {
        "title": "Administrative Order 2023-01 - Protocols for Entry into the Washington, D.C. Courthouse and In-Person Court Proceedings in Other Locations (REPEALED)",
        "name": "Administrative_Order_2023-01_Repealed.pdf",
    },
    {
        "title": "Administrative Order 2022-01 - Protocols for Entry into the Washington, D.C. Courthouse and In-Person Court Proceedings in Other Locations (REPEALED)",
        "name": "Administrative_Order_2022-01_Repealed.pdf",
    },
    {
        "title": "Administrative Order 2021-03 - Protocol for Court Personnel and Contractors Entry into Washington, D.C. Courthouse (REPEALED)",
        "name": "Administrative_Order_2021-03_REPEALED.pdf",
    },
    {
        "title": "Administrative Order 2021-02 - Washington, DC Courthouse Access (REPEALED)",
        "name": "Administrative_Order_2021-02_REPEALED.pdf",
    },
    {
        "title": "Administrative Order 2021-01 - Policies for Remote (Virtual) Proceedings",
        "name": "Administrative_Order_2021-01.pdf",
    },
    {
        "title": "Administrative Order 2020-05 - Digital Image Signatures on Paper Copies During the Transition to the New Case Management System",
        "name": "Administrative_Order_2020-05.pdf",
    },
    {
        "title": "Administrative Order 2020-04 - Answer Filing Deadline During the Transition to a New Case Management System",
        "name": "Administrative_Order_2020-04.pdf",
    },
    {
        "title": "Administrative Order 2020-03 - Limited Entry of Appearance Procedures",
        "name": "Administrative_Order_2020-03.pdf",
    },
    {
        "title": "Administrative Order 2020-02 - Remote Court Proceedings During COVID-19 Pandemic",
        "name": "Administrative_Order_2020-02.pdf",
    },
    {
        "title": "Administrative Order 2020-01 - Postponement of 2020 Nonattorney Examination",
        "name": "Administrative_Order_2020-01.pdf",
    },
]


class AdministrativeOrdersPageInitializer(PageInitializer):
    """
    Creates/updates an AdministrativeOrdersPage under the Home page
    and populates its pdf_section StreamField with multiple PDFs.
    """

    def __init__(self):
        super().__init__()
        self.slug = "administrative-orders"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        title = "Administrative Orders"

        # Check if page exists
        existing = Page.objects.filter(slug=self.slug).first()
        if existing:
            logger.info(f"- '{title}' page already exists.")
            return existing

        logger.info(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(AdministrativeOrdersPage)

        new_page = home_page.add_child(
            instance=AdministrativeOrdersPage(
                title=title,
                slug=self.slug,
                seo_title="Administrative Orders",
                content_type=content_type,
                body="",
                search_description="Administrative Orders from 2020 through 2024.",
            )
        )

        for file_detail in ADMIN_ORDERS_DATA:
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=file_detail["name"],
                title=file_detail["title"],
            )
            if document:
                pdf_entry = PDFs(pdf=document, page=new_page)
                pdf_entry.save()
                logger.info(f"   - Loaded document: {file_detail['name']}")
            else:
                logger.info(
                    f"   - **Failed** to load document: {file_detail['name']}"
                )

        logger.info(f"Successfully created the '{title}' page.")
        new_page.save()
