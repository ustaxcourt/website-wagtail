from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage


order_docs = {
    "TC-16-90001.pdf": {"title": "TC-16-90001.pdf", "file": None},
    "TC-16-90002.pdf": {"title": "TC-16-90002.pdf", "file": None},
    "TC-16-90002_2017-08-16_Council-Order.pdf": {
        "title": "TC-16-90002_2017-08-16_Council-Order.pdf",
        "file": None,
    },
    "TC-16-90003.pdf": {"title": "TC-16-90003.pdf", "file": None},
    "TC-16-90003_2017-08-16_Council-Order.pdf": {
        "title": "TC-16-90003_2017-08-16_Council-Order.pdf",
        "file": None,
    },
    "TC-16-90004.pdf": {"title": "TC-16-90004.pdf", "file": None},
    "TC-17-90001.pdf": {"title": "TC-17-90001.pdf", "file": None},
    "TC-17-900011.pdf": {"title": "TC-17-900011.pdf", "file": None},
    "TC-17-900012.pdf": {"title": "TC-17-900012.pdf", "file": None},
    "TC-17-900015.pdf": {"title": "TC-17-900015.pdf", "file": None},
    "TC-17-90003.pdf": {"title": "TC-17-90003.pdf", "file": None},
    "TC-17-90003_2017-08-16_Council_Order.pdf": {
        "title": "TC-17-90003_2017-08-16_Council_Order.pdf",
        "file": None,
    },
    "TC-17-90004.pdf": {"title": "TC-17-90004.pdf", "file": None},
    "TC-17-90005.pdf": {"title": "TC-17-90005.pdf", "file": None},
    "TC-17-90005_2018-08.06_Council_Order.pdf": {
        "title": "TC-17-90005_2018-08.06_Council_Order.pdf",
        "file": None,
    },
    "TC-17-90006.pdf": {"title": "TC-17-90006.pdf", "file": None},
    "TC-17-90006_2018-08.06_Council_Order.pdf": {
        "title": "TC-17-90006_2018-08.06_Council_Order.pdf",
        "file": None,
    },
    "TC-17-90007.pdf": {"title": "TC-17-90007.pdf", "file": None},
    "TC-17-90008.pdf": {"title": "TC-17-90008.pdf", "file": None},
    "TC-17-90009.pdf": {"title": "TC-17-90009.pdf", "file": None},
    "TC-17-90010.pdf": {"title": "TC-17-90010.pdf", "file": None},
    "TC-17-90011_2018-08.06_Council_Order.pdf": {
        "title": "TC-17-90011_2018-08.06_Council_Order.pdf",
        "file": None,
    },
    "TC-17-90013.pdf": {"title": "TC-17-90013.pdf", "file": None},
    "TC-17-90015_2018-08.06_Council_Order.pdf": {
        "title": "TC-17-90015_2018-08.06_Council_Order.pdf",
        "file": None,
    },
    "TC-18-90001.pdf": {"title": "TC-18-90001.pdf", "file": None},
    "TC-18-90001_2018-12.17_Council_Order.pdf": {
        "title": "TC-18-90001_2018-12.17_Council_Order.pdf",
        "file": None,
    },
    "TC-19-90003.pdf": {"title": "TC-19-90003.pdf", "file": None},
    "TC-20-90001.pdf": {"title": "TC-20-90001.pdf", "file": None},
    "TC-20-90002.pdf": {"title": "TC-20-90002.pdf", "file": None},
    "TC-21-90001.pdf": {"title": "TC-21-90001.pdf", "file": None},
    "TC-21-90002.pdf": {"title": "TC-21-90002.pdf", "file": None},
    "TC-21-90003.pdf": {"title": "TC-21-90003.pdf", "file": None},
    "TC-21-90004.pdf": {"title": "TC-21-90004.pdf", "file": None},
    "TC-21-90005.pdf": {"title": "TC-21-90005.pdf", "file": None},
    "TC-21-90006.pdf": {"title": "TC-21-90006.pdf", "file": None},
    "TC-21-90007.pdf": {"title": "TC-21-90007.pdf", "file": None},
    "TC-21-90008.pdf": {"title": "TC-21-90008.pdf", "file": None},
    "TC-21-90009.pdf": {"title": "TC-21-90009.pdf", "file": None},
    "TC-22-90001.pdf": {"title": "TC-22-90001.pdf", "file": None},
    "TC-23-90001.pdf": {"title": "TC-23-90001.pdf", "file": None},
    "TC-23-90002.pdf": {"title": "TC-23-90002.pdf", "file": None},
    "TC-24-90001-CJ-1.pdf": {"title": "TC-24-90001-CJ-1.pdf", "file": None},
    "TC-24-90001-CJ-2.pdf": {"title": "TC-24-90001-CJ-2.pdf", "file": None},
    "TC-24-90001-JCDC-1.pdf": {"title": "TC-24-90001-JCDC-1.pdf", "file": None},
    "TC-24-90001-JCDC-2.pdf": {"title": "TC-24-90001-JCDC-2.pdf", "file": None},
    "TC-24-90002.pdf": {"title": "TC-24-90002.pdf", "file": None},
    "TC-24-90003.pdf": {"title": "TC-24-90003.pdf", "file": None},
    "TC-24-90004.pdf": {"title": "TC-24-90004.pdf", "file": None},
    "TC-24-90005.pdf": {"title": "TC-24-90005.pdf", "file": None},
    "TC-24-90007.pdf": {"title": "TC-24-90007.pdf", "file": None},
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

        for name in order_docs:
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=order_docs[name],
                title=order_docs[name][title],
            )
            order_docs[name]["file"] = uploaded_document.file

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": "The effective date of the Tax Court’s Judicial Conduct and Disability Procedures was June 15, 2016. Links to orders issued pursuant to these procedures will be added to this page when they are issued.",
                    },
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
