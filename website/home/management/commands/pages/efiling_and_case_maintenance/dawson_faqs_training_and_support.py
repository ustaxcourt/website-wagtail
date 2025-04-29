from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, NavigationRibbon

from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)
import logging

logger = logging.getLogger(__name__)

dawson_faqs_training_and_support_doc = {
    "DAWSON_Public_Training_Guide.pdf": "",
    "DAWSON_Petitioner_Training_Guide.pdf": "",
    "DAWSON_Practitioner_Training_Guide.pdf": "",
}


class DawsonFaqsTrainingAndSupportPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-faqs-training-and-support"
        title = "Frequently Asked Questions About DAWSON"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=dawson_faqs_ribbon_name
        ).first()

        for document in dawson_faqs_training_and_support_doc.keys():
            uploaded_document = self.load_document_from_documents_dir(None, document)
            dawson_faqs_training_and_support_doc[document] = uploaded_document.file.url

            body_content = [
                {"type": "h2", "value": "DAWSON: Training and Support"},
                {
                    "type": "questionanswers",
                    "value": [
                        {
                            "question": "Where do I find DAWSON training and user guides?",
                            "answer": f"""The <strong><a target="_blank" href="/dawson" title="DAWSON">DAWSON</a></strong>
                            page has helpful information, including this <strong><a href="https://us02web.zoom.us/rec/play/EZTpkvLfDeXoLeW2YzhdTgpBcKoC10NumGESfgR2Aorw_E85V6vwwpCCmQOEzW9GI9M-0fvLZTxMPr_T.wWcxq5k6tZ3GI8OP" title="DAWSON Training Video">training video</a></strong>.
                            <ul>
                                <li><strong><a href="{dawson_faqs_training_and_support_doc["DAWSON_Public_Training_Guide.pdf"]}" target="_blank" title="DAWSON Public Training Guide">DAWSON Public Training Guide: DAWSON_Public_Training_Guide.pdf</a></strong></li>
                                <li><strong><a href="{dawson_faqs_training_and_support_doc["DAWSON_Petitioner_Training_Guide.pdf"]}" target="_blank" title="DAWSON Public Training Guide"> DAWSON Self-Represented (Pro Se) Training Guide: DAWSON_Petitioner_Training_Guide.pdf</a></strong></li>
                                <li><strong><a href="{dawson_faqs_training_and_support_doc["DAWSON_Practitioner_Training_Guide.pdf"]}" target="_blank" title="DAWSON Public Training Guide">DAWSON Practitioner Training Guide: DAWSON_Practitioner_Training_Guide.pdf</a></strong></li>
                            </ul>""",
                            "anchortag": "FAQS1",
                        },
                        {
                            "question": "Who do I contact for help with DAWSON?",
                            "answer": """<ul>
                                          <li>If you need DAWSON assistance, email <a href=\"mailto:dawson.support@ustaxcourt.gov\" title=\"Contact DAWSON Support\">dawson.support@ustaxcourt.gov</a>. (Documents sent to that email address cannot be filed on your behalf).</li>
                                          <li>User feedback and error reporting can also be submitted to <strong><a href=\"mailto:dawson.support@ustaxcourt.gov\" title=\"Contact DAWSON Support\">dawson.support@ustaxcourt.gov</a></strong>.</li>
                                          <li>The Court’s main number is <a href=\"tel:+12025210700\">(202) 521-0700</a>.</li>
                                          </ul>""",
                            "anchortag": "FAQS2",
                        },
                    ],
                },
            ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="DAWSON: Training and Support",
                body=body_content,
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
