from home.models import CallToActionBox
from home.management.commands.pages.page_initializer import PageInitializer
from wagtail.documents.models import Document
import logging

logger = logging.getLogger(__name__)

snippet_name = "Ready to begin your petition?"
arrow_forward_name = "Arrow Forward"


# This initializes the Call To Action Box snippet named "Ready to begin your petition?".
# It extends PageInitializer to give it access to the load_document_from_documents_dir method.
class CallToActionBoxInitializer(PageInitializer):
    def __init__(self):
        self.logger = logger

    def create(self):
        if CallToActionBox.objects.filter(header=snippet_name).exists():
            logger.info("'Ready to begin your petition?' already exists.")
            return

        logger.info("Creating the 'Ready to begin your petition?' Call to Action Box.")

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

        call_to_action_box = CallToActionBox(
            header=snippet_name,
            body='<h2 data-block-key="kyfpj">Once you have your documents ready, start your petition through DAWSON, the Court'
            "s electronic filing system.</h2>",
            buttons=[
                {
                    "type": "button",
                    "value": {
                        "icon": None,
                        "icon_location": "before",
                        "text": "View Pre-Filing Checklist",
                        "url": [
                            {
                                "type": "external_url",
                                "value": "/petitioners-prepare-to-file",
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
            ],
        )
        call_to_action_box.save()
