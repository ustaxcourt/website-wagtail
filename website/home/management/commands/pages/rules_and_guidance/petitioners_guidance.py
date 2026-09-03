from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
import logging
from urllib.parse import urljoin
from home.models.utils.execute_script import ExecuteScript
from django.conf import settings
from wagtail.documents.models import Document


logger = logging.getLogger(__name__)
arrow_forward_name = "Arrow Forward"


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
        _base_url = getattr(settings, "BASE_URL", "")

        arrow_forward_doc = Document.objects.filter(title=arrow_forward_name).first()
        if arrow_forward_doc:
            logger.info("'Arrow Forward' icon already exists.")
        else:
            logger.info("Creating the 'Arrow Forward' icon.")
            arrow_forward_doc = self.load_document_from_documents_dir(
                subdirectory=None,
                filename="arrow_forward.svg",
                title="Arrow Forward",
            )

        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                introductory_text="“Pro Se” (pronounced pro say) means representing yourself without an attorney or other authorized practitioner.",
                call_to_action=_cta_box,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                body=[
                    {
                        "type": "hero_section",
                        "value": {
                            "title": "File Your Petition with the United States Tax Court",
                            "introductory_text": "Challenge an IRS determination by filing a petition. This guide walks you through every step of the process, including what to expect after filing in the United States Tax Court.",
                            "callout_block": {
                                "heading": "Deadline for Filing",
                                "text": '<p data-block-key="dj49o">A document filed through DAWSON is timely if it is electronically filed by 11:59 p.m., Eastern time, on the day it is due.</p>',
                                "callout_type": "info",
                            },
                            "buttons": [
                                {
                                    "type": "button",
                                    "value": {
                                        "icon": None,
                                        "icon_location": "before",
                                        "text": "View Pre-Filing Checklist",
                                        "url": [
                                            {
                                                "type": "external_url",
                                                "value": urljoin(
                                                    _base_url,
                                                    "/petitioners-prepare-to-file",
                                                ),
                                                "id": "75b8ede0-6600-4f4d-9083-65ddb9f45454",
                                            }
                                        ],
                                        "style": "inverted-primary",
                                        "button_hover": True,
                                    },
                                    "id": "9f41e5e3-6cb0-4570-aa47-9492917159c1",
                                },
                                {
                                    "type": "button",
                                    "value": {
                                        "icon": arrow_forward_doc.pk,
                                        "icon_location": "after",
                                        "text": "File a Petition Online",
                                        "url": [
                                            {
                                                "type": "external_url",
                                                "value": "https://app.dawson.ustaxcourt.gov/login",
                                                "id": "3e90ea52-62a0-40eb-a809-bf428812b729",
                                            }
                                        ],
                                        "style": "primary",
                                        "button_hover": True,
                                    },
                                    "id": "36b20544-d1ee-4464-82de-fac53d20dc43",
                                },
                            ],
                        },
                        "id": "359b2e61-baf5-4473-9110-d5460ce9538a",
                    }
                ],
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
