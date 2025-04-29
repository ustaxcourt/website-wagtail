from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)

reports_and_statistics_docs = {
    "appellate_report_april_2021.pdf": "",
    "appellate_report_april_2022.pdf": "",
    "appellate_report_april_2023.pdf": "",
    "appellate_report_april_2024.pdf": "",
    "appellate_report_august_2020.pdf": "",
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
    "appellate_report_for_january_2022.pdf": "",
    "appellate_report_january_2023.pdf": "",
    "appellate_report_january_2024.pdf": "",
    "appellate_report_january_2025.pdf": "",
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
    "appellate_report_may_2024.pdf": "",
    "appellate_report_november_2020.pdf": "",
    "appellate_report_november_2021.pdf": "",
    "appellate_report_november_2022.pdf": "",
    "appellate_report_november_2023.pdf": "",
    "appellate_report_november_2024.pdf": "",
    "appellate_report_october_2020.pdf": "",
    "appellate_report_october_2021.pdf": "",
    "appellate_report_october_2022.pdf": "",
    "appellate_report_october_2023.pdf": "",
    "appellate_report_october_2024.pdf": "",
    "appellate_report_september_2020.pdf": "",
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
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "reports-and-statistics"
        title = "Reports & Statistics"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for doc_name in reports_and_statistics_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            reports_and_statistics_docs[doc_name] = document

        home_page.add_child(
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
                    {"type": "h2", "value": "Appellate Reports"},
                    {"type": "h3", "value": "2025"},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, February 2025",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_february_2025.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, January 2025",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_january_2025.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                    {
                        "type": "h3",
                        "value": "2024",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, December 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_december_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, November 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_november_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, October 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_october_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, September 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_september_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, August 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_august_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, July 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_july_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, June 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_june_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, May 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_may_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, April 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_april_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, March 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_march_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, February 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_february_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, January 2024",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_january_2024.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                    {
                        "type": "h3",
                        "value": "2023",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, December 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_december_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, November 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_november_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, October 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_october_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, September 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_september_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, August 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_august_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, July 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_july_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, June 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_june_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, April 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_april_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, March 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_march_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, February 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_february_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, January 2023",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_january_2023.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                    {
                        "type": "h3",
                        "value": "2022",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, December 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_december_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, November 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_november_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, October 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_october_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, September 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_september_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, August 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_august_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, July 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_july_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, June 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_june_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, April 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_april_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, March 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_march_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, February 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_february_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, January 2022",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_for_january_2022.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                    {
                        "type": "h3",
                        "value": "2021",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, December 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_december_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, November 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_november_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, October 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_october_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, September 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_september_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, August 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_august_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, July 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_july_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, June 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_june_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, April 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_april_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, March 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_march_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, February 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_february_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, January 2021",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_january_2021.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                    {
                        "type": "h3",
                        "value": "2020",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, November 2020",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_november_2020.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, October 2020",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_october_2020.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, September 2020",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_september_2020.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, August 2020",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_august_2020.pdf"
                                    ].id,
                                    "url": None,
                                },
                                {
                                    "title": "Cases Commenced in the Courts of Appeals, July 2020",
                                    "icon": IconCategories.PDF,
                                    "document": reports_and_statistics_docs[
                                        "appellate_report_july_2020.pdf"
                                    ].id,
                                    "url": None,
                                },
                            ]
                        },
                    },
                ],
                show_in_menus=True,
            )
        )
