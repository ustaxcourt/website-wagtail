from django.conf import settings
from home.models import CallToActionBox
from home.management.commands.pages.page_initializer import PageInitializer
from wagtail.documents.models import Document
from home.models.utils.execute_script import ExecuteScript
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

snippet_name = "Ready to begin your petition?"
arrow_forward_name = "Arrow Forward"


# This initializes the Call To Action Box snippet named "Ready to begin your petition?".
# It extends PageInitializer to give it access to the load_document_from_documents_dir method.
class CallToActionBoxInitializer(PageInitializer):
    def __init__(self):
        self.logger = logger

    def _get_arrow_forward_document(self):
        arrow_forward_doc = Document.objects.filter(title=arrow_forward_name).first()
        if arrow_forward_doc:
            logger.info("'Arrow Forward' icon already exists.")
            return arrow_forward_doc

        logger.info("Creating the 'Arrow Forward' icon.")
        return self.load_document_from_documents_dir(
            subdirectory=None,
            filename="arrow_forward.svg",
            title="Arrow Forward",
        )

    def _build_buttons(self):
        _base_url = getattr(settings, "BASE_URL", "")
        arrow_forward_doc = self._get_arrow_forward_document()

        return [
            {
                "type": "button",
                "value": {
                    "icon": None,
                    "icon_location": "before",
                    "text": "View Pre-Filing Checklist",
                    "url": [
                        {
                            "type": "external_url",
                            "value": urljoin(_base_url, "/petitioners-prepare-to-file"),
                            "id": "9258b09c-d243-415a-b250-7beca1295b41",
                        }
                    ],
                    "style": "inverted-primary",
                    "button_hover": True,
                },
                "id": "f20dbe9a-bfe3-4627-93af-36dafd1a04b9",
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
                            "id": "3893a3f0-8c63-4c19-80ed-3ef9e523267f",
                        }
                    ],
                    "style": "primary",
                    "button_hover": True,
                },
                "id": "9751ae42-071f-4c7a-b5f4-9f07d66844ed",
            },
        ]

    def _get_target_box(self):
        return (
            CallToActionBox.objects.filter(header=snippet_name).order_by("pk").first()
        )

    def _upsert_target_box(self):
        defaults = {
            "body": "Once you have your documents ready, start your petition through DAWSON, the Court's electronic filing system.",
            "buttons": self._build_buttons(),
        }

        call_to_action_box = self._get_target_box()
        if call_to_action_box:
            for field, value in defaults.items():
                setattr(call_to_action_box, field, value)
            call_to_action_box.save()
            logger.info("Updated the '%s' Call to Action Box.", snippet_name)
            return call_to_action_box

        call_to_action_box = CallToActionBox(header=snippet_name, **defaults)
        call_to_action_box.save()
        logger.info("Successfully created Call to Action Box.")
        return call_to_action_box

    def create(self):
        if settings.SITE_IS_LIVE and not self._get_target_box():
            logger.info(
                "Skipping Call to Action Box creation. Call to Action Box creation/recreation suppressed past site LIVE DATE."
            )
            return

        logger.info("Creating or updating Call to Action Box...")
        self._upsert_target_box()

    def update(self):
        logger.info("Updating Call to Action Box...")
        self.create()

    def run(self):
        """Update the Call to Action Box as an execution script"""
        command_name = "Call to Action Box update for Petition Experience redesign"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.update()
            execution_log_text = (
                "Call to Action Box updated for Petition Experience redesign"
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
