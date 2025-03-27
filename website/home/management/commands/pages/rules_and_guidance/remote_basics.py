from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage
from home.management.commands.snippets.zoomgov_proceeding_ribbon import (
    remote_proceedings_ribbon_name,
)


class RemoteBasicsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "zoomgov-the-basics"
        title = "Zoomgov Proceedings"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=remote_proceedings_ribbon_name
        ).first()

        questions = [
            {
                "question": "Do I come to the courthouse for a Zoomgov proceeding?",
                "answer": "No. All Zoomgov proceedings will be held remotely. Do not come to the courthouse.",
                "anchortag": "ZOOM1",
            },
            {
                "question": "What if I don't have access to the Internet?",
                "answer": "You will need to inform the Judge as soon as possible. You may be able to participate by telephone.",
                "anchortag": "ZOOM2",
            },
            {
                "question": "What if I don't have access to a computer, smartphone, or tablet?",
                "answer": "You will need to inform the Judge as soon as possible. You may be able to participate by telephone.",
                "anchortag": "ZOOM3",
            },
            {
                "question": "Are Zoomgov proceedings and Zoomgov meetings the same thing?",
                "answer": "<ul><li>Zoomgov “proceedings”, which include trials, hearings, and sometimes conferences, are the same as Zoomgov “meetings”.</li><li>The “Meeting ID” is the proceedings code.</li></ul>",
                "anchortag": "ZOOM4",
            },
            {
                "question": "Are Zoomgov and Zoom the same?",
                "answer": "Essentially, yes. They work the same for the participants. Zoomgov is designed specifically to accommodate sensitive government business, but participants will not see the difference.",
                "anchortag": "ZOOM5",
            },
            {
                "question": "Do I need a Zoom account to participate in a Zoomgov proceeding?",
                "answer": "No. You do not need your own account to connect to a Zoomgov proceeding.",
                "anchortag": "ZOOM6",
            },
            {
                "question": "Is there a fee to participate in a Zoomgov proceeding?",
                "answer": "No. There is no cost for participants.",
                "anchortag": "ZOOM7",
            },
            {
                "question": "Do I have to get dressed up?",
                "answer": "Zoomgov proceedings are official Court proceedings, and you should dress as you would for any other Court appearance.",
                "anchortag": "ZOOM8",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Zoomgov FAQs: The Basics",
                body=[
                    {"type": "h2", "value": "Zoomgov FAQs: The Basics"},
                    {"type": "questionanswers", "value": questions},
                ],
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
