from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage


order_docs = {
    "TC-16-90001.pdf": {"title": "06/01/2017 - TC-16-90001", "file": None},
    "TC-16-90002.pdf": {"title": "06/01/2017 - TC-16-90002", "file": None},
    "TC-16-90002_2017-08-16_Council-Order.pdf": {
        "title": "08/17/2017 - TC-16-90002",
        "file": None,
    },
    "TC-16-90003.pdf": {"title": "06/01/2017 - TC-16-90003", "file": None},
    "TC-16-90003_2017-08-16_Council-Order.pdf": {
        "title": "08/17/2017 - TC-16-90003",
        "file": None,
    },
    "TC-16-90004.pdf": {"title": "06/01/2017 - TC-16-90004", "file": None},
    "TC-17-90001.pdf": {"title": "06/01/2017 - TC-17-90001", "file": None},
    "TC-17-900011.pdf": {"title": "12/21/2017 - TC-17-900011", "file": None},
    "TC-17-900012.pdf": {"title": "12/21/2017 - TC-17-900012", "file": None},
    "TC-17-900015.pdf": {"title": "12/21/2017 - TC-17-900015", "file": None},
    "TC-17-90003.pdf": {"title": "06/01/2017 - TC-17-90003", "file": None},
    "TC-17-90003_2017-08-16_Council_Order.pdf": {
        "title": "08/17/2017 - TC-17-90003",
        "file": None,
    },
    "TC-17-90004.pdf": {"title": "06/01/2017 - TC-17-90004", "file": None},
    "TC-17-90005.pdf": {"title": "12/21/2017 - TC-17-90005", "file": None},
    "TC-17-90005_2018-08.06_Council_Order.pdf": {
        "title": "08/06/2018 - TC-17-90005",
        "file": None,
    },
    "TC-17-90006.pdf": {"title": "12/21/2017 - TC-17-90006", "file": None},
    "TC-17-90006_2018-08.06_Council_Order.pdf": {
        "title": "08/06/2018 - TC-17-90006",
        "file": None,
    },
    "TC-17-90007.pdf": {"title": "12/21/2017 - TC-17-90007", "file": None},
    "TC-17-90008.pdf": {"title": "04/06/2018 - TC-17-90008", "file": None},
    "TC-17-90009.pdf": {"title": "04/06/2018 - TC-17-90009", "file": None},
    "TC-17-90010.pdf": {"title": "04/06/2018 - TC-17-90010", "file": None},
    "TC-17-90013.pdf": {"title": "04/19/2018 - TC-17-90013", "file": None},
    "TC-17-90011_2018-08.06_Council_Order.pdf": {
        "title": "08/06/2018 - TC-17-90011",
        "file": None,
    },
    "TC-17-90015_2018-08.06_Council_Order.pdf": {
        "title": "08/06/2018 - TC-17-90015",
        "file": None,
    },
    "TC-18-90001.pdf": {"title": "10/31/2018 - TC-18-90001", "file": None},
    "TC-18-90001_2018-12.17_Council_Order.pdf": {
        "title": "12/17/2018 - TC-18-90001",
        "file": None,
    },
    # "TC-19-90001.pdf": {"title": "02/22/2019 - TC-19-90001", "file": None},
    # "TC-19-90002.pdf": {"title": "06/25/2019 - TC-19-90002", "file": None},
    "TC-19-90003.pdf": {"title": "01/27/2020 - TC-19-90003", "file": None},
    "TC-20-90001.pdf": {"title": "11/16/2020 - TC-20-90001", "file": None},
    "TC-20-90002.pdf": {"title": "05/13/2021 - TC-20-90002", "file": None},
    "TC-21-90001.pdf": {"title": "05/18/2021 - TC-21-90001", "file": None},
    "TC-21-90002.pdf": {"title": "05/13/2021 - TC-21-90002", "file": None},
    "TC-21-90003.pdf": {"title": "02/09/2022 - TC-21-90003", "file": None},
    "TC-21-90004.pdf": {"title": "02/09/2022 - TC-21-90004", "file": None},
    "TC-21-90005.pdf": {"title": "02/09/2022 - TC-21-90005", "file": None},
    "TC-21-90006.pdf": {"title": "02/09/2022 - TC-21-90006", "file": None},
    "TC-21-90007.pdf": {"title": "02/16/2022 - TC-21-90007", "file": None},
    "TC-21-90008.pdf": {"title": "02/16/2022 - TC-21-90008", "file": None},
    "TC-21-90009.pdf": {"title": "02/11/2022 - TC-21-90009", "file": None},
    "TC-22-90001.pdf": {"title": "07/26/2022 - TC-22-90001", "file": None},
    "TC-23-90001.pdf": {"title": "06/12/2023 - TC-23-90001", "file": None},
    "TC-23-90002.pdf": {"title": "06/12/2023 - TC-23-90002", "file": None},
    "TC-24-90001-CJ-1.pdf": {"title": "03/22/2024 - TC-24-90001-1", "file": None},
    "TC-24-90001-CJ-2.pdf": {"title": "03/22/2024 - TC-24-90001-2", "file": None},
    "TC-24-90001-JCDC-1.pdf": {"title": "08/16/2024 - TC-24-90001-1", "file": None},
    "TC-24-90001-JCDC-2.pdf": {"title": "08/16/2024 - TC-24-90001-2", "file": None},
    "TC-24-90002.pdf": {"title": "03/28/2024 - TC-24-90002", "file": None},
    "TC-24-90003.pdf": {"title": "06/06/2024 - TC-24-90003", "file": None},
    "TC-24-90004.pdf": {"title": "06/06/2024 - TC-24-90004", "file": None},
    "TC-24-90005.pdf": {"title": "06/06/2024 - TC-24-90005", "file": None},
    "TC-24-90007.pdf": {"title": "11/15/2024 - TC-24-90007", "file": None},
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
                filename=name,
                title=order_docs[name]["title"],
                collection="Judicial Conduct and Disability Procedures",
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
