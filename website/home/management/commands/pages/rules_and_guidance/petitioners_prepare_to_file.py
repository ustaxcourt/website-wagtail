from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class PetitionersPrepareToFilePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-prepare-to-file"
        title = "Prepare to File"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        _snippet_name = "Ready to begin your petition?"
        _cta_box = CallToActionBox.objects.filter(header=_snippet_name).first()
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                introductory_text='<p data-block-key="hjrzp">The United States Tax Court encourages electronic filing through DAWSON, the court’s electronic filing and case management system. </p><p data-block-key="b3i0k"><b>Note:</b> If filing using DAWSON, once you start this process you won’t be able to save your work and come back to it. Petitioners who file by paper cannot immediately switch to electronic access. To protect your information, the Court will mail identity verification instructions to your address of record. Switching to electronic access will be available only after the verification process is complete. Consider filing electronically from the start to get electronic access to your case immediately.</p>',
                call_to_action=_cta_box,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")

    def run(self):
        """Update the Petitioners Prepare to File page."""
        command_name = "Initialize Petitioners Prepare to File page"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
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
