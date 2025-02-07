from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon, IconCategories
from home.models import EnhancedStandardPage


class PetitionersStartPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners_start"
        title = "Guidance for Petitioners: Starting A Case"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Blue Navigation Bar"
        ).first()

        questions = [
            "How do I start a case in the Tax Court?",
            "Who can file a petition with the Tax Court?",
            "Is there anyone who can help me file a petition and/or help me in my case against the IRS?",
            "How can I find a tax clinic?",
            "If I want to represent myself or if I don’t qualify for representation by a tax clinic, can I represent myself?",
            "What should I do if I don’t speak and/or understand English very well?",
            "Are there any circumstances where the Court will help pay for the cost of an interpreter at trial?",
            "If I need an interpreter at trial what should I do?",
            "I thought I came to an agreement with the IRS, but the IRS sent me a notice of deficiency or a notice of determination stating that I have a right to file a petition with the Tax Court. Should I file a petition even though I thought my case was settled?",
            "If I decide to file a petition, what is the next step?",
            "How do I fill out my petition?",
            "How do I decide whether to elect regular or small tax case procedures?",
            "What should I say in my petition?",
            "When should I file my petition?",
            "How do I file my petition?",
            "How can I protect the privacy of my Social Security number?",
            "How can I protect the privacy of personal information such as my financial account numbers?",
            "How do I delete or redact my Social Security number or other private numbers from documents?",
            "What if I forget to redact or delete personal information?",
            "May I file my petition electronically or by fax?",
            "How do I ensure that the petition is filed on time?",
            "My petition is due today. Is it too late to file a petition with the Tax Court?",
            "Does it cost anything to file a petition?",
            "Are there any circumstances where I do not have to pay the $60 filing fee?",
            "Must I pay the amount of tax that the IRS says I owe while my case is pending in the Tax Court?",
            "Should I include anything else with my petition?",
            "Should I send anything else to the Tax Court when I file my petition?",
            "Where may I request a place of trial if I elected to conduct my case as a small tax case?",
            "Where may I request a place of trial if I elected to conduct my case as a regular tax case?",
            "May I request trial in a more conveniently located city outside my state?",
            "May I request that my case be heard remotely?",
            "How can I be sure that I have done everything correctly?",
            "What can I do if I forgot to say everything I wanted to in my petition?",
            "After I file my petition, how many copies of any documents should I send the Tax Court if I decide I want to file anything else?",
            "What happens after I file my petition?",
            "How can I check on the status of my case?",
            "Who can I contact if I have questions?",
            "Someone told me that if I want to ask the Tax Court to take some action affecting the other party, I should file a motion. What is a motion?",
            "What are some of the common motions that can be filed?",
            "What is a motion for summary judgment? How should I respond to one?",
            "I would like to file a motion but I’m not sure what to title it. Will the Court correct the title of a motion (or other document) that is titled incorrectly?",
            "Where do I send responses to motions?",
            "I filed a timely petition with the Tax Court in a deficiency case. I received a letter from the IRS seeking to assess or collect the tax for the same tax year(s) I petitioned. What should I do?",
            "What should I do if I receive a “no change” letter from the IRS after I file a petition in the Tax Court?",
            "What happens if I can’t find my copy of a document filed with the Tax Court?",
            "What if I move or change my address after I file a petition?",
        ]

        links = [
            {
                "title": question,
                "icon": IconCategories.INFO_CIRCLE_FILLED,
                "document": None,
                "url": f"#START{i+1}",
            }
            for i, question in enumerate(questions)
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Resources about the Court's Zoomgov remote proceedings",
                body=[
                    {"type": "heading", "value": "Starting A Case"},
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "This guide provides information, but not legal advice, for individuals who represent themselves before the Tax Court. It answers some of taxpayers' most frequent questions. It is a brief step-by-step explanation of the process of:",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": links,
                        },
                    },
                    {"type": "hr", "value": True},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
