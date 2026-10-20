from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
import logging
from home.models.utils.execute_script import ExecuteScript
from home.models.pages.petitioner_experience import PetitionerExperiencePage


logger = logging.getLogger(__name__)


class DawsonHowToViewDashboard(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-how-to-view-dashboard"
        title = "How to view the DAWSON dashboard"

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                introductory_text="<p>Learn how to view the DAWSON dashboard</p>",
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
            )
        )

        new_page.save_revision().publish()

    def run(self):
        """Update the Dawson How to view the DAWSON dashboard"""
        command_name = "WAG-1450: How to view the DAWSON dashboard"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            execution_log_text = (
                "Dawson How to view the DAWSON dashboard page updated successfully."
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
