from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.management.commands.pages.rules_and_guidance.side_card_seed_data import (
    add_clerks_office_side_card,
    add_need_legal_help_side_card,
)
from home.models import NavigationRibbon
from home.models import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class PetitionersPrepareToFilePageInitializer(PageInitializer):
    COMMAND_NAME = "Initialize Petitioners Prepare to File page"

    def __init__(self):
        super().__init__()
        self.slug = "petitioners-prepare-to-file"
        self.title = "Prepare to File"

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

        _snippet_name = "Ready to begin your petition?"
        _cta_box = CallToActionBox.objects.filter(header=_snippet_name).first()
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=self.title,
                introductory_text='<p data-block-key="hjrzp">The United States Tax Court encourages electronic filing through DAWSON, the court’s electronic filing and case management system. </p><p data-block-key="b3i0k"><b>Note:</b> If filing using DAWSON, once you start this process you won’t be able to save your work and come back to it. Petitioners who file by paper cannot immediately switch to electronic access. To protect your information, the Court will mail identity verification instructions to your address of record. Switching to electronic access will be available only after the verification process is complete. Consider filing electronically from the start to get electronic access to your case immediately.</p>',
                call_to_action=_cta_box,
                slug=self.slug,
                seo_title=self.title,
                navigation_ribbon=navigation_ribbon,
                search_description=self.title,
            )
        )
        add_clerks_office_side_card(self, new_page)
        add_need_legal_help_side_card(self, new_page)

        # SideCards are InlinePanel children stored in revision content, so
        # publish only after attaching them - otherwise the editor loads a
        # revision without them and the next save would delete the cards.
        new_page.save_revision().publish()

        logger.info(f"Created the '{self.title}' page.")

    def update(self):
        """Delete and recreate the Prepare to File page.

        The "only run once per environment" guard lives in run(), which
        checks ExecuteScript.command_exists() *before* creating the marker
        row and only then calls this method - so this method must not
        repeat that check itself. (It briefly did: run() creates the marker
        before calling update(), so a check here would always see the
        marker as already existing and skip every time, silently turning
        this into a no-op. WAG-1339 caught this because the FAQs page's
        Helpful Links card - seeded the same way - depends on pages created
        later in the same script run, so it needs this recreate to actually
        happen.)
        """
        existing_page = Page.objects.filter(slug=self.slug).first()
        if existing_page:
            logger.info(f"Deleting existing '{self.title}' page to recreate it.")
            existing_page.delete()

        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def run(self):
        """Update the Petitioners Prepare to File page."""
        # Check if script already exists
        if ExecuteScript.command_exists(self.COMMAND_NAME):
            logger.info(f"Script '{self.COMMAND_NAME}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(self.COMMAND_NAME)

        try:
            self.update()
            execution_log_text = (
                "Petitioners Prepare to File page updated successfully."
            )
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
