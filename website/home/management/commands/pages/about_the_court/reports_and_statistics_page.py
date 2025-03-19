from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories, NavigationCategories
from home.models import EnhancedStandardPage

reports_and_statistics_docs = {
    "appellate_report_april_2021.pdf": "",
    "appellate_report_april_2022.pdf": "",
    "appellate_report_april_2023.pdf": "",
    "appellate_report_april_2024.pdf": "",
    "appellate_report_august_2021.pdf": "",
    "appellate_report_august_2022.pdf": "",
    "appellate_report_august_2023.pdf": "",
    "appellate_report_august_2024.pdf": "",
    "appellate_report_december_2021.pdf": "",
    "appellate_report_december_2022.pdf": "",
    "appellate_report_december_2023.pdf": "",
    "appellate_report_december_2024.pdf": "",
    "appellate_report_february_2021.pdf": "",
    "appellate_report_february_2022.pdf": "",
    "appellate_report_february_2023.pdf": "",
    "appellate_report_february_2024.pdf": "",
    "appellate_report_february_2025.pdf": "",
    "appellate_report_january_2021.pdf": "",
    "appellate_report_january_2022.pdf": "",
    "appellate_report_january_2023.pdf": "",
    "appellate_report_july_2020.pdf": "",
    "appellate_report_july_2021.pdf": "",
    "appellate_report_july_2022.pdf": "",
    "appellate_report_july_2023.pdf": "",
    "appellate_report_july_2024.pdf": "",
    "appellate_report_june_2021.pdf": "",
    "appellate_report_june_2022.pdf": "",
    "appellate_report_june_2023.pdf": "",
    "appellate_report_june_2024.pdf": "",
    "appellate_report_march_2021.pdf": "",
    "appellate_report_march_2022.pdf": "",
    "appellate_report_march_2023.pdf": "",
    "appellate_report_march_2024.pdf": "",
    "appellate_report_may_2021.pdf": "",
    "appellate_report_may_2022.pdf": "",
    "appellate_report_may_2023.pdf": "",
    "appellate_report_may_2024.pdf": "",
    "appellate_report_november_2020.pdf": "",
    "appellate_report_november_2021.pdf": "",
    "appellate_report_november_2022.pdf": "",
    "appellate_report_november_2023.pdf": "",
    "appellate_report_november_2024.pdf": "",
    "appellate_report_october_2021.pdf": "",
    "appellate_report_october_2022.pdf": "",
    "appellate_report_october_2023.pdf": "",
    "appellate_report_october_2024.pdf": "",
    "appellate_report_september_2021.pdf": "",
    "appellate_report_september_2022.pdf": "",
    "appellate_report_september_2023.pdf": "",
    "appellate_report_september_2024.pdf": "",
    "FY_2021_Congressional_Budget_Justification.pdf": "",
    "FY_2022_Congressional_Budget_Justification.pdf": "",
    "FY_2023_Congressional_Budget_Justification.pdf": "",
    "FY_2024_Congressional_Budget_Justification.pdf": "",
    "FY_2025_Congressional_Budget_Justification.pdf": "",
    "USTC_IRA_Strategic_Plan_2024.pdf": "",
}


class ReportsAndStatisticsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "reports-and-statistics"
        title = "Reports & Statistics"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for doc_name in reports_and_statistics_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            reports_and_statistics_docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Reports & Statistics",
                body=[
                    {
                        "type": "h2",
                        "value": "Congressional Budget Justification Reports",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "USTC IRA Strategic Plan",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "USTC_IRA_Strategic_Plan_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "FY 2025 Congressional Budget Justification",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "FY_2025_Congressional_Budget_Justification.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "FY 2024 Congressional Budget Justification",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "FY_2024_Congressional_Budget_Justification.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "FY 2023 Congressional Budget Justification",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "FY_2023_Congressional_Budget_Justification.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "FY 2022 Congressional Budget Justification",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "FY_2022_Congressional_Budget_Justification.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "FY 2021 Congressional Budget Justification",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "FY_2021_Congressional_Budget_Justification.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Appellate Reports",
                    },
                    {"type": "h3", "value": "2025"},
                ],
                show_in_menus=True,
            )
        )

        EnhancedStandardPage.objects.filter(id=new_page.id).update(
            menu_item_name="Reports & Statistics",
            navigation_category=NavigationCategories.ABOUT_THE_COURT,
        )
