from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging
from home.models.utils.execute_script import ExecuteScript


logger = logging.getLogger(__name__)


class PetitionersGuidancePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-guidance"
        title = "Guidance for Self-Represented Petitioners (Pro Se)"

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
                introductory_text="“Pro Se” (pronounced pro say) means representing yourself without an attorney or other authorized practitioner.",
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
        """Update the Petitioners Guidance page."""
        command_name = "Initialize Petitioners Guidance page"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            execution_log_text = "Petitioners Guidance page updated successfully."
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
