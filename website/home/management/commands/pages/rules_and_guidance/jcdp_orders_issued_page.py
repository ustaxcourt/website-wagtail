from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, IconCategories


chief_judge_2024_docs = [
    {"title": "11/15/2024 - TC-24-90007", "document": "TC-24-90007.pdf"},
    {"title": "06/06/2024 - TC-24-90005", "document": "TC-24-90005.pdf"},
    {"title": "06/06/2024 - TC-24-90004", "document": "TC-24-90004.pdf"},
    {"title": "06/06/2024 - TC-24-90003", "document": "TC-24-90003.pdf"},
    {"title": "03/28/2024 - TC-24-90002", "document": "TC-24-90002.pdf"},
    {"title": "03/22/2024 - TC-24-90001-1", "document": "TC-24-90001-CJ-1.pdf"},
    {"title": "03/22/2024 - TC-24-90001-2", "document": "TC-24-90001-CJ-2.pdf"},
    {"title": "02/01/2024 - TC-23-90003", "document": "TC-23-90002.pdf"},  # Check this.
]

chief_judge_2023_docs = [
    {"title": "06/12/2023 - TC-23-90002", "document": "TC-23-90002.pdf"},
    {"title": "06/12/2023 - TC-23-90001", "document": "TC-23-90001.pdf"},
]

chief_judge_2022_docs = [
    {"title": "07/26/2022 - TC-22-90001", "document": "TC-22-90001.pdf"},
    {"title": "02/16/2022 - TC-21-90008", "document": "TC-21-90008.pdf"},
    {"title": "02/16/2022 - TC-21-90007", "document": "TC-21-90007.pdf"},
    {"title": "02/11/2022 - TC-21-90009", "document": "TC-21-90009.pdf"},
    {"title": "02/09/2022 - TC-21-90006", "document": "TC-21-90006.pdf"},
    {"title": "02/09/2022 - TC-21-90005", "document": "TC-21-90005.pdf"},
    {"title": "02/09/2022 - TC-21-90004", "document": "TC-21-90004.pdf"},
    {"title": "02/09/2022 - TC-21-90003", "document": "TC-21-90003.pdf"},
]

chief_judge_2021_docs = [
    {"title": "05/18/2021 - TC-21-90001", "document": "TC-21-90001.pdf"},
    {"title": "05/13/2021 - TC-21-90002", "document": "TC-21-90002.pdf"},
    {"title": "05/13/2021 - TC-20-90002", "document": "TC-20-90002.pdf"},
]

chief_judge_2020_docs = [
    {"title": "11/16/2020 - TC-20-90001", "document": "TC-20-90001.pdf"},
]

chief_judge_2019_docs = [
    {"title": "12/19/2019 - TC-19-90003", "document": "TC-19-90003.pdf"},
    {"title": "06/25/2019 - TC-19-90002", "document": "TC-19-90003.pdf"},  # Check this.
    {"title": "02/22/2019 - TC-19-90001", "document": "TC-19-90003.pdf"},  # Check this.
]

chief_judge_2018_docs = [
    {"title": "10/31/2018 - TC-18-90001", "document": "TC-18-90001.pdf"},
    {"title": "04/19/2018 - TC-17-90013", "document": "TC-17-90013.pdf"},
    {"title": "04/06/2018 - TC-17-90008", "document": "TC-17-90008.pdf"},
    {"title": "04/06/2018 - TC-17-90009", "document": "TC-17-90009.pdf"},
    {"title": "04/06/2018 - TC-17-90010", "document": "TC-17-90010.pdf"},
]

chief_judge_2017_docs = [
    {"title": "12/21/2017 - TC-17-90005", "document": "TC-17-90005.pdf"},
    {"title": "12/21/2017 - TC-17-90006", "document": "TC-17-90006.pdf"},
    {"title": "12/21/2017 - TC-17-90007", "document": "TC-17-90007.pdf"},
    {"title": "12/21/2017 - TC-17-900011", "document": "TC-17-900011.pdf"},
    {"title": "12/21/2017 - TC-17-900012", "document": "TC-17-900012.pdf"},
    {"title": "12/21/2017 - TC-17-900015", "document": "TC-17-900015.pdf"},
    {"title": "06/01/2017 - TC-16-90001", "document": "TC-16-90001.pdf"},
    {"title": "06/01/2017 - TC-16-90002", "document": "TC-16-90002.pdf"},
    {"title": "06/01/2017 - TC-16-90003", "document": "TC-16-90003.pdf"},
    {"title": "06/01/2017 - TC-16-90004", "document": "TC-16-90004.pdf"},
    {"title": "06/01/2017 - TC-17-90001", "document": "TC-17-90001.pdf"},
    {"title": "06/01/2017 - TC-17-90003", "document": "TC-17-90003.pdf"},
    {"title": "06/01/2017 - TC-17-90004", "document": "TC-17-90004.pdf"},
]

council_2024_docs = [
    {"title": "08/16/2024 - TC-24-90001-1", "document": "TC-24-90001-1.pdf"},
    {"title": "08/16/2024 - TC-24-90001-2", "document": "TC-24-90001-2.pdf"},
]

council_2020_docs = [
    {"title": "01/27/2020 - TC-19-90003", "document": "TC-19-90003.pdf"},
]

council_2019_docs = [
    {"title": "12/18/2019 - TC-17-90014", "document": "TC-17-90014.pdf"},
    {"title": "07/02/2019 - TC-17-90002", "document": "TC-17-90002.pdf"},
]

council_2018_docs = [
    {"title": "12/17/2018 - TC-18-90001", "document": "TC-18-90001.pdf"},
    {"title": "08/06/2018 - TC-17-90005", "document": "TC-17-90005.pdf"},
    {"title": "08/06/2018 - TC-17-90006", "document": "TC-17-90006.pdf"},
    {"title": "08/06/2018 - TC-17-90011", "document": "TC-17-90011.pdf"},
    {"title": "08/06/2018 - TC-17-90015", "document": "TC-17-90015.pdf"},
]

council_2017_docs = [
    {"title": "08/17/2017 - TC-16-90002", "document": "TC-16-90002.pdf"},
    {"title": "08/17/2017 - TC-16-90003", "document": "TC-16-90003.pdf"},
    {"title": "08/17/2017 - TC-17-90003", "document": "TC-17-90003.pdf"},
]


class JCDPOrdersIssuedStartPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def load_order_docs(self, docs):
        info_links = []

        for info in docs:
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=info["document"],
                title=info["title"],
                collection="Judicial Conduct and Disability Procedures",
            )

            info_links.append(
                {
                    "title": info["title"],
                    "icon": IconCategories.PDF,
                    "document": document.id,
                    "url": None,
                }
            )
        return info_links

    def create_page_info(self, home_page):
        slug = "jcdp_orders_issued"
        title = "Orders Issued in Judicial Conduct and Disability Cases"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        chief_judge_column = [
            {
                "type": "h2",
                "value": "Chief Judge:",
            },
            {
                "type": "h3",
                "value": "2024",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2024_docs),
                },
            },
            {
                "type": "h3",
                "value": "2023",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2023_docs),
                },
            },
            {
                "type": "h3",
                "value": "2022",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2022_docs),
                },
            },
            {
                "type": "h3",
                "value": "2021",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2021_docs),
                },
            },
            {
                "type": "h3",
                "value": "2020",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2020_docs),
                },
            },
            {
                "type": "h3",
                "value": "2019",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2019_docs),
                },
            },
            {
                "type": "h3",
                "value": "2018",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2018_docs),
                },
            },
            {
                "type": "h3",
                "value": "2017",
            },
            {
                "type": "links",
                "value": {
                    "links": self.load_order_docs(chief_judge_2017_docs),
                },
            },
        ]

        council_column = []

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
                    {
                        "type": "columns",
                        "value": {"column": [chief_judge_column, council_column]},
                    },
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
