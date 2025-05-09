from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage
from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)
import logging

logger = logging.getLogger(__name__)

dawson_faqs_docs = {
    "Rule-26_Amended_03202023.pdf": "",
}


class DawsonFaqsAccountManagementPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-faqs-account-management"
        title = "Frequently Asked Questions About DAWSON"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=dawson_faqs_ribbon_name
        ).first()

        for document in dawson_faqs_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )
            dawson_faqs_docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "Who can register for a DAWSON account?",
                "answer": """<ul>
                              <li>Only parties with active cases and practitioners admitted to the Tax Court Bar may register for a DAWSON account.</li>
                              <li>Anyone can access the Court's daily opinions, as well as orders search, through the Court's website without a DAWSON account. See Searches and Public Access, below.</li>
                              </ul>""",
                "anchortag": "FAQS1",
            },
            {
                "question": "Do I need a DAWSON account?",
                "answer": f"""<ul>
                              <li>If you are a party, you will need a DAWSON account for free electronic access to your Court records.</li>
                                 <ul>
                                 <li>If you do not have a DAWSON account, you will receive case documents from the Court by U.S. mail instead of being able to access them electronically.</li>
                                 </ul>
                              <li>If you are admitted to practice before the Court, you are generally required to file documents and receive service electronically. See
                              <strong><a href="{dawson_faqs_docs["Rule-26_Amended_03202023.pdf"]}" target="_blank" title="Rule 26(b)">Rule 26(b)</a></strong>, Tax Court Rules of Practice and Procedure. Electronic filing and the electronic service of Court filings will take place through DAWSON.</li>
                                <ul>
                                 <li>Petitions may, but are not required to be, filed electronically.</li>
                                 </ul>
                              </ul>""",
                "anchortag": "FAQS2",
            },
            {
                "question": "How do I get a DAWSON account?",
                "answer": """<ul>
                                <li>Self-represented petitioners who file a petition electronically will register for a DAWSON account before filing their petition. Petitioners who do not file their petitions electronically, or did not have an account in the prior eAccess system, can establish DAWSON credentials by emailing
                                <strong><a href="mailto:dawson.support@ustaxcourt.gov" title="Contact DAWSON Support">dawson.support@ustaxcourt.gov</a></strong>.</li>
                                   <ul>
                                   <li>There is no need to submit another copy of your petition if you mailed it and later get DAWSON access.</li>
                                   </ul>
                                   <li>The Court will provide newly admitted practitioners with DAWSON credentials when they are assigned a Tax Court Bar number.</li>
                                    <li>Practitioners who did not receive or did not timely activate their temporary DAWSON credentials can request new credentials by emailing <strong><a href="mailto:dawson.support@ustaxcourt.gov" title="Contact DAWSON Support">dawson.support@ustaxcourt.gov</a></strong>.
                                    </li>
                                   <ul>
                                   <li>Do not register for a DAWSON account through the registration process.</li>
                                   </ul>
                                </ul>""",
                "anchortag": "FAQS3",
            },
            {
                "question": "If I had an eAccess account, will I need a new DAWSON account?",
                "answer": """<ul>
                                <li>Yes. Your eAccess credentials will not work in the new system.</li>
                                <li>In late 2020, temporary DAWSON credentials were emailed to eAccess system users, including petitioners and practitioners. If you did not receive yours, or did not activate them timely, emaill <strong><a href="mailto:dawson.support@ustaxcourt.gov" title="Contact DAWSON Support">dawson.support@ustaxcourt.gov</a></strong>.</li>
                                </ul>""",
                "anchortag": "FAQS4",
            },
            {
                "question": "If I currently have a PACER account, will I need a DAWSON account?",
                "answer": "Yes. DAWSON is not connected to PACER.",
                "anchortag": "FAQS5",
            },
            {
                "question": "Can I reset my DAWSON password?",
                "answer": """Yes. On the DAWSON log-in screen, click on "Forgot your password?" and follow the instructions to reset your password. For more information, see the <strong><a href="/dawson-user-guides" target="_blank" title="User Guides">User Guides</a></strong>.""",
                "anchortag": "FAQS6",
            },
            {
                "question": "How do I change my contact information?",
                "answer": """<ul>
                              <li>Practitioners can update their contact information by clicking on the "Person Icon" and then "My Account" in the upper right corner of the DAWSON screen.</li>
                                 <ul>
                                 <li>Changing your email address in DAWSON will change both your service email and your login email. Only one email address per account is permitted. Email addresses are case-sensitive.</li>
                                 <li>NOTE: IRS Practitioners should contact <strong><a href="mailto:admissions@ustaxcourt.gov" title="admissions@ustaxcourt.gov">admissions@ustaxcourt.gov</a></strong> for updates to contact information</li>
                                 <li>Petitioners can update their email address by clicking on the "Person Icon" and then "My Account" in the upper right corner of the DAWSON screen.</li>
                                 <li>NOTE that changing your email address in DAWSON will change both your service email and your login email. Only one email address per account is permitted. Email addresses are case-sensitive.</li>
                                </ul>
                                 <li>Petitioners can update their mailing address and phone number by updating the Case Information in each of their cases.</li>
                                 <li>Please refer to the <strong><a href="/dawson-user-guides" target="_blank" title="DAWSON User Guides">User Guides</a></strong> for more detailed instructions.</li>
                                 </ul>
                              </ul>""",
                "anchortag": "FAQS7",
            },
            {
                "question": "Can I add an additional email address for someone else to receive a message when a document has been served in a case?",
                "answer": "No. The Court serves documents only on the parties, the participants, or their representatives at their addresses of record.",
                "anchortag": "FAQS8",
            },
            {
                "question": "Can I change my firm name?",
                "answer": """Contact <strong><a href="mailto:dawson.support@ustaxcourt.gov" title="Contact DAWSON Support">dawson.support@ustaxcourt.gov</a></strong> for assistance in updating your firm name.""",
                "anchortag": "FAQS9",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="DAWSON: Account Management",
                body=[
                    {"type": "h2", "value": "DAWSON: Account Management"},
                    {"type": "questionanswers", "value": questions},
                ],
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
