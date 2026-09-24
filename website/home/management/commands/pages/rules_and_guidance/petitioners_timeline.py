from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class PetitionersTimelinePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-timeline"
        title = "Process and Timeline"

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
                introductory_text="What to expect during the tax court process, what documents you will need, links to forms, and a checklist to use.",
                call_to_action=_cta_box,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                body=[
                    {
                        "type": "summary_timeline",
                        "value": {
                            "title": "TYPICAL CASE TIMELINE",
                            "phases": [
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "File Petition",
                                        "date_range": "Day 0-Deadline",
                                    },
                                    "id": "0e88e4c5-a9c6-49a5-9181-d9103c991a0d",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "IRS Answer",
                                        "date_range": "~60 days",
                                    },
                                    "id": "035ef5a0-94a6-4022-98c1-aa65490c272a",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "Pre-Trial",
                                        "date_range": "2-12 months",
                                    },
                                    "id": "312473bc-6f85-41c7-a12c-c913d16029be",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "Trial",
                                        "date_range": "12-24+ months",
                                    },
                                    "id": "50c5f9c3-9f47-4776-b98a-e1de5b4b0b3e",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "Decision",
                                        "date_range": "6-12+ months",
                                    },
                                    "id": "81478e67-3c14-4339-a5a2-d1f12aa85f04",
                                },
                            ],
                        },
                        "id": "8c34cf67-1a49-4da5-a508-f35217759926",
                    },
                    {
                        "type": "detailed_timeline",
                        "value": {
                            "title": "United States Tax Court Case Timeline",
                            "introduction": '<p data-block-key="lamyb">Please note: The timeline of every court case is different. This is a general timeline to help you<br/>understand the lifecycle of a case and should not be used for planning purposes.</p>',
                            "phases": [
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Receive an IRS Notice",
                                        "date_range": "Day 0",
                                    },
                                    "id": "b4941d41-ab20-4e73-9ea6-66e6a22001fb",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "File Your Petition",
                                        "date_range": "Day 0-Deadline",
                                    },
                                    "id": "36557146-a5db-462b-9955-a436cd87d486",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "IRS Files Answer",
                                        "date_range": "Up To 60 Days After the Petition is Filed",
                                    },
                                    "id": "96ce579b-89c6-4b01-9013-e33a079314dc",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Trial Date is Scheduled",
                                        "date_range": "6-13 Months",
                                    },
                                    "id": "c711466a-53f8-4deb-aa63-a0edb2b05cb2",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Discovery & Discussion",
                                        "date_range": "4-12 Months",
                                    },
                                    "id": "90c53c79-43a6-45d7-b384-a067bc4355e3",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Trial Preparation",
                                        "date_range": "2-4 Months Before Trial",
                                    },
                                    "id": "92fbd6bf-b338-4993-a5e7-ddffe874c42b",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Trial",
                                        "date_range": "12-24+ Months After Filing",
                                    },
                                    "id": "49330a63-e33a-4028-9104-32063c7541c0",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Decision",
                                        "date_range": "6-12+ Months After Trial",
                                    },
                                    "id": "6c4a7579-026c-444a-ae78-41d71ce33e7a",
                                },
                            ],
                        },
                        "id": "b050e963-8231-4c33-817c-101d50838d56",
                    },
                ],
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")

    def run(self):
        """Update the Petitioners Timeline page."""
        command_name = "Initialize Petitioners Timeline page"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            execution_log_text = "Petitioners Timeline page updated successfully."
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
