from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)

terms_of_use_docs = {
    "Rule-21.pdf": "",
}


class DawsonTermsOfUsePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "dawson-tou"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Terms of Use"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        # Load Rule 21 document
        for document in terms_of_use_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )
            terms_of_use_docs[document] = uploaded_document.file.url

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": f"Acceptance of the Terms of Use constitutes an agreement to abide by all Court Rules, policies, and procedures governing the use of the Court's electronic access and filing system (DAWSON). By registering for DAWSON, practitioners and petitioners consent to receive electronic service (eService) of documents pursuant to <strong><a href='{terms_of_use_docs['Rule-21.pdf']}' target='_blank'>Rule 21(b)(1)(D)</a></strong>. The notification of service to all parties and persons in the case who have consented to electronic service in conjunction with the entry on the Court's docket record constitutes service on all parties who have consented to electronic service. Practitioners and petitioners who consent to receive eService agree to regularly log on to DAWSON to view served documents. The combination of user name and password serves as the signature of the individual filing the documents. Individuals must protect the security of their login credentials and immediately notify the Court by emailing <strong><a href='mailto:dawson.support@ustaxcourt.gov'>dawson.support@ustaxcourt.gov</a></strong> if they learn that their account has been compromised. The Terms of Use can be changed at any time without notice.",
                    },
                    {
                        "type": "paragraph",
                        "value": "Acknowledgment of Policies and Procedures",
                    },
                    {"type": "paragraph", "value": "I understand that:"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": f"I must provide accurate and complete information when I register for electronic access to DAWSON. I must promptly notify the Court of any changes to that information. See also <strong><a href='{terms_of_use_docs['Rule-21.pdf']}' target='_blank'>Rule 21(b)(4)</a></strong>."
                                },
                                {
                                    "text": "Registration is for my and my authorized agent's use only, and I am responsible for preventing unauthorized use of my user name and password. If I believe there has been unauthorized use, I must notify the Court by emailing <strong><a href='mailto:dawson.support@ustaxcourt.gov'>dawson.support@ustaxcourt.gov</a></strong>."
                                },
                            ],
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": "The United States Tax Court reserves the right to deny, limit, or suspend access to DAWSON to anyone: (1) Who provides information that is fraudulent, (2) whose usage has the potential to cause disruption to the system; or (3) who in the judgment of the Court is misusing the system.",
                    },
                ],
                search_description="Terms of Use for DAWSON - The United States Tax Court's electronic access and filing system",
            )
        )

        new_page.save_revision().publish()
        logger.info(f"Successfully created the '{title}' page.")
