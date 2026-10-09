from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.management.commands.pages.rules_and_guidance.side_card_seed_data import (
    add_clerks_office_side_card,
    add_helpful_links_side_card,
    add_need_legal_help_side_card,
)
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.snippets.faq_filter_tag import FAQFilterTag
import logging
from home.models.utils.execute_script import ExecuteScript


logger = logging.getLogger(__name__)

# Placeholder Q&As until final FAQ content is provided. Every seeded FilterTag is
# used, some more than once, and their first appearances follow the mockup's
# button order: Filing, Deadlines, Representation, Forms & Documents,
# Trial Process, Fees & Costs, After Decision.
PLACEHOLDER_ANSWER = (
    "<p>Placeholder answer. Final content for this question will be added in a "
    "future update.</p>"
)
PLACEHOLDER_QUESTIONS = [
    (
        "filing",
        "how-do-i-file",
        "How do I file a petition with the United States Tax Court?",
    ),
    ("deadlines", "petition-deadline", "What is the deadline to file a petition?"),
    ("deadlines", "missed-deadline", "What happens if I miss the deadline?"),
    ("filing", "small-tax-case", "What is a small tax case?"),
    ("representation", "represent-myself", "Can I represent myself in Tax Court?"),
    ("representation", "legal-help", "Can I get legal help?"),
    ("forms-documents", "forms-needed", "What forms do I need to file a petition?"),
    ("trial-process", "trial-location", "Where will my trial be held?"),
    ("trial-process", "settle-case", "Can I settle my case without going to trial?"),
    ("fees-costs", "filing-fee", "How much does it cost to file a petition?"),
    ("after-decision", "appeal-decision", "Can I appeal a Tax Court decision?"),
]


class PetitionersHelpPageInitializer(PageInitializer):
    COMMAND_NAME = "WAG-1343: Add FAQs with filter section to Petitioners Help page"

    def __init__(self):
        super().__init__()
        self.slug = "petitioners-help"
        self.title = "Frequently Asked Questions"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {self.title} page already exists.")
            return

        logger.info(f"Creating the '{self.title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        # No call_to_action, unlike the other Petitioners pages: the mockup has none.
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=self.title,
                body=self.build_body(),
                slug=self.slug,
                seo_title=self.title,
                navigation_ribbon=navigation_ribbon,
                search_description=self.title,
            )
        )
        add_helpful_links_side_card(self, new_page)
        add_clerks_office_side_card(self, new_page)
        add_need_legal_help_side_card(self, new_page)

        # SideCards are InlinePanel children stored in revision content, so
        # publish only after attaching them - otherwise the editor loads a
        # revision without them and the next save would delete the cards.
        new_page.save_revision().publish()

        logger.info(f"Created the '{self.title}' page.")

    def build_body(self):
        live_slugs = set(
            FAQFilterTag.objects.filter(live=True).values_list("slug", flat=True)
        )
        questions = []
        for slug, anchortag, question in PLACEHOLDER_QUESTIONS:
            if slug not in live_slugs:
                logger.warning(
                    f"FAQ FilterTag '{slug}' not found; skipping '{question}'."
                )
                continue
            questions.append(
                {
                    "question": question,
                    "answer": PLACEHOLDER_ANSWER,
                    "anchortag": anchortag,
                    "filtertag": slug,
                }
            )
        return [
            {
                "type": "questionanswers",
                "value": {"display_filter_section": True, "questions": questions},
            }
        ]

    def update(self):
        """Delete and recreate the Petitioners Help page.

        The "only run once per environment" guard lives in run(), which
        creates the marker row *before* calling this method - so this method
        must not repeat that check itself, or it would always see the marker
        and silently skip. The recreate matters because the Helpful Links
        card depends on pages created later in the same script run.
        """
        existing_page = Page.objects.filter(slug=self.slug).first()
        if existing_page:
            logger.info(f"Deleting existing '{self.title}' page to recreate it.")
            existing_page.delete()

        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def run(self):
        """Update the Petitioners Help page."""
        if ExecuteScript.command_exists(self.COMMAND_NAME):
            logger.info(f"Script '{self.COMMAND_NAME}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(self.COMMAND_NAME)

        try:
            self.update()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = "Petitioners Help page updated successfully."
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
