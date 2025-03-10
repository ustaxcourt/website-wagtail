from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    NavigationRibbon,
    EnhancedStandardPage,
)
from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)


class SearchesAndPublicAccessPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson_faqs_searches_public_access"
        title = "Frequently Asked Questions About DAWSON"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=dawson_faqs_ribbon_name
        ).first()

        questions = [
            {
                "question": "What search functionality does DAWSON have?",
                "answer": """<ul>
            <li>The ability to search for cases by first, last, or full name or docket number is available.</li>
            <li>The ability to search by part of a name (e.g., entering “Ron” for Ronald) is expected to be available in the future.</li>
            <li>The ability to search for orders by keyword or phrase, docket number, case title/petitioner name, judge, or date is available in DAWSON.</li>
            <li>The ability to search for opinions by keyword or phrase, docket number, case title/petitioner name, judge, type of opinion, or date is available in DAWSON.</li>
            <li>The ability to search for practitioners by name or U.S. Tax Court bar number.</li>
            </ul>""",
                "anchortag": "START1",
            },
            {
                "question": "Where do I find the opinions released today?",
                "answer": """<ul>
            <li>Opinions will be posted to the Court’s website on days they are released. See <strong><a href="https://dawson.ustaxcourt.gov/todays-opinions" title="Today’s Opinions">Today’s Opinions.</a></strong></li>
            <li>Cases consolidated for trial, briefing, and opinion will show the opinions listed separately by each docket number.</li>
            </ul>""",
                "anchortag": "START2",
            },
            {
                "question": "Where do I find the orders released today?",
                "answer": """<ul>
            <li>Orders will be posted to the Court’s website on days they are released. See <strong><a href="https://dawson.ustaxcourt.gov/todays-orders" title="Today’s Orders">Today’s Orders</a></strong>.</li>
            <li>All orders issued by the Court on a particular day will be made available as they are served.</li>
            <li>The “Today’s Orders” listing will be populated with the most recent orders at the top.</li>
            </ul>""",
                "anchortag": "START3",
            },
            {
                "question": "How do I link to an order or opinion?",
                "answer": "For security purposes, DAWSON generates unique links every time an item is viewed. To retain an Order or Opinion, save a copy of the document. To reference an opinion or order without saving a copy, link to the docket record of the case, where the order or opinion can be viewed.",
                "anchortag": "START4",
            },
            {
                "question": "What documents are viewable electronically by the general public?",
                "answer": """<ul>
             <li>Opinions and orders issued by the Court.</li>
             <li>Post-trial briefs e-Filed by practitioners on or after August 1, 2023.</li>
             <li>Amicus briefs filed on or after August 1, 2023.</li>
             <li>Stipulated Decisions filed on or after August 1, 2023.</li>
             <li>Documents in sealed cases, or individual documents that are sealed, <strong>are not viewable</strong> other than by the parties.</li>
             </ul>""",
                "anchortag": "START5",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Search and Public Access",
                body=[
                    {"type": "h2", "value": "DAWSON: Searches and Public Access"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=True,
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
