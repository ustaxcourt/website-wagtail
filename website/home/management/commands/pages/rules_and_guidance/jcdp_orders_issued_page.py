from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage


petitioners_docs = {
    "TC-16-90001.pdf": None,
    "TC-16-90002.pdf": None,
    "TC-16-90002_2017-08-16_Council-Order.pdf": None,
    "TC-16-90003.pdf": None,
    "TC-16-90003_2017-08-16_Council-Order.pdf": None,
    "TC-16-90004.pdf": None,
    "TC-17-90001.pdf": None,
    "TC-17-900011.pdf": None,
    "TC-17-900012.pdf": None,
    "TC-17-900015.pdf": None,
    "TC-17-90003.pdf": None,
    "TC-17-90003_2017-08-16_Council_Order.pdf": None,
    "TC-17-90004.pdf": None,
    "TC-17-90005.pdf": None,
    "TC-17-90005_2018-08.06_Council_Order.pdf": None,
    "TC-17-90006.pdf": None,
    "TC-17-90006_2018-08.06_Council_Order.pdf": None,
    "TC-17-90007.pdf": None,
    "TC-17-90008.pdf": None,
    "TC-17-90009.pdf": None,
    "TC-17-90010.pdf": None,
    "TC-17-90011_2018-08.06_Council_Order.pdf": None,
    "TC-17-90013.pdf": None,
    "TC-17-90015_2018-08.06_Council_Order.pdf": None,
    "TC-18-90001.pdf": None,
    "TC-18-90001_2018-12.17_Council_Order.pdf": None,
    "TC-19-90003.pdf": None,
    "TC-20-90001.pdf": None,
    "TC-20-90002.pdf": None,
    "TC-21-90001.pdf": None,
    "TC-21-90002.pdf": None,
    "TC-21-90003.pdf": None,
    "TC-21-90004.pdf": None,
    "TC-21-90005.pdf": None,
    "TC-21-90006.pdf": None,
    "TC-21-90007.pdf": None,
    "TC-21-90008.pdf": None,
    "TC-21-90009.pdf": None,
    "TC-22-90001.pdf": None,
    "TC-23-90001.pdf": None,
    "TC-23-90002.pdf": None,
    "TC-24-90001-CJ-1.pdf": None,
    "TC-24-90001-CJ-2.pdf": None,
    "TC-24-90001-JCDC-1.pdf": None,
    "TC-24-90001-JCDC-2.pdf": None,
    "TC-24-90002.pdf": None,
    "TC-24-90003.pdf": None,
    "TC-24-90004.pdf": None,
    "TC-24-90005.pdf": None,
    "TC-24-90007.pdf": None,
}


class JCDPOrdersIssuedStartPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "jcdp_orders_issued"
        title = "Orders Issued in Judicial Conduct and Disability Cases"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for document in petitioners_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(None, document)
            petitioners_docs[document] = uploaded_document.file.url

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Guidance for Petitioners - Starting a Case",
                body=[
                    {"type": "h2", "value": "Starting A Case"},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
