from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page
from home.models import AdministrativeOrdersPage, NavigationCategories
from home.management.commands.pages.page_initializer import PageInitializer

# Example PDF data
ADMIN_ORDERS_DATA = [
    "Administrative_Order_2020-01.pdf",
    "Administrative_Order_2020-02.pdf",
    "Administrative_Order_2020-03.pdf",
    "Administrative_Order_2020-04.pdf",
    "Administrative_Order_2020-05.pdf",
    "Administrative_Order_2021-02_REPEALED.pdf",
    "Administrative_Order_2021-03_REPEALED.pdf",
    "Administrative_Order_2022-01_Repealed.pdf",
    "Administrative_Order_2023-01_Repealed.pdf",
    "Administrative_Order_2023-02.pdf",
    "Administrative_Order_2024-01.pdf",
]


class AdministrativeOrdersPageInitializer(PageInitializer):
    """
    Creates/updates an AdministrativeOrdersPage under the Home page
    and populates its pdf_section StreamField with multiple PDFs.
    """

    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "administrative_orders"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
            admin_orders_page = self.create_administrative_orders_page(home_page)

            # Now populate that page’s pdf_section StreamField with our PDF docs.
            self.populate_pdf_section(admin_orders_page)

        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

    def create_administrative_orders_page(self, parent_page):
        """Create the AdministrativeOrdersPage if it doesn’t exist; otherwise return the existing one."""
        title = "Administrative Orders"

        # Check if page exists
        existing = Page.objects.filter(slug=self.slug).first()
        if existing:
            self.logger.write(f"- '{title}' page already exists.")
            return existing

        self.logger.write(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(AdministrativeOrdersPage)

        new_page = parent_page.add_child(
            instance=AdministrativeOrdersPage(
                title=title,
                slug=self.slug,
                seo_title="Administrative Orders",
                show_in_menus=True,
                content_type=content_type,
                body="",
                search_description="Administrative Orders from 2020 through 2024.",
            )
        )

        # Optionally set the custom navigation fields (if you’re using them)
        AdministrativeOrdersPage.objects.filter(id=new_page.id).update(
            menu_item_name="ADMINISTRATIVE ORDERS",
            navigation_category=NavigationCategories.RULES_AND_GUIDANCE,
        )

        self.logger.write(f"Successfully created the '{title}' page.")
        return new_page

    def populate_pdf_section(self, page_instance):
        """
        Loads all PDFs from the 'administrative_orders' folder and
        adds them into the page’s StreamField (pdf_section).
        """
        pdf_data_list = []
        for filename in ADMIN_ORDERS_DATA:
            document = self.load_document_from_documents_dir(
                subdirectory="administrative_orders",
                filename=filename,
                title=filename,
            )
            if document:
                pdf_data_list.append({"id": document.id})
                self.logger.write(f"   - Loaded document: {filename}")
            else:
                self.logger.write(f"   - **Failed** to load document: {filename}")

        pdf_section_data = [
            {
                "type": "pdf_section",
                "value": {
                    "section_title": None,
                    "pdfs": pdf_data_list,
                    "ordering": "asc",
                },
            }
        ]

        page_instance.pdf_section = pdf_section_data
        page_instance.save_revision().publish()
