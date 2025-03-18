from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage
from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)


class DawsonFaqsBasicsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-faqs-basics"
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
                "question": "What is DAWSON?",
                "answer": "The U.S. Tax Court's case management system, DAWSON (Docket Access Within a Secure Online Network), is an electronic filing and case management system designed to make it easier for parties and the Court to start a Tax Court case, file and process documents, and manage cases.",
                "anchortag": "FAQS1",
            },
            {
                "question": "Will additional features be added to DAWSON?",
                "answer": """ <ul>
                              <li>Additional features and system enhancements to DAWSON will be rolled out on an ongoing basis.</li>
                              <li>The version of DAWSON launched on December 28, 2020, prioritized functionality necessary for parties to manage their cases and for the Court to operate efficiently.</li>
                              <li>Check the Court's website for up-to-date information, including release notes.</li>
                              </ul>""",
                "anchortag": "FAQS2",
            },
            {
                "question": "How much does it cost to use DAWSON?",
                "answer": """<ul>
                              <li>DAWSON is free to all users.</li>
                              <li>Parties have free access to their cases with no limit on their ability to download files from their cases.</li>
                              <li>Non-parties have free access to docket records, orders, and opinions in unsealed cases.</li>
                              </ul>""",
                "anchortag": "FAQS3",
            },
            {
                "question": "How do I access DAWSON?",
                "answer": """DAWSON can be accessed from a computer, smartphone, or tablet by going to the Court's
                 <strong><a href="https://www.ustaxcourt.gov/" target="_blank" title="United States Tax Court">website</a></strong>
                  or to <strong><a href="https://dawson.ustaxcourt.gov" target="_blank" title="DAWSON">https://dawson.ustaxcourt.gov/</a></strong>.""",
                "anchortag": "FAQS4",
            },
            {
                "question": "How do I check to see if DAWSON is working properly?",
                "answer": """For information regarding system status, please visit <strong><a href="https://status.ustaxcourt.gov/" target="_blank" title="DAWSON Status">https://status.ustaxcourt.gov/</a></strong>.""",
                "anchortag": "FAQS5",
            },
            {
                "question": "Do I need special software to access DAWSON?",
                "answer": "No. DAWSON is web-based, so all you need is access to the internet and a current internet browser.",
                "anchortag": "FAQS6",
            },
            {
                "question": "Is DAWSON compatible with all internet browsers?",
                "answer": "DAWSON is compatible with most up-to-date browsers such as Chrome, Edge, Firefox, or Safari. It is not compatible with outdated browsers such as Internet Explorer.",
                "anchortag": "FAQS7",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="DAWSON: The Basics",
                body=[
                    {"type": "h2", "value": "DAWSON: The Basics"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
