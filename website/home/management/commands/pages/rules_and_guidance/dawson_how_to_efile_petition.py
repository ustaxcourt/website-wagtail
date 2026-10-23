import logging

from wagtail.documents.models import Document
from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from search.dawson_client import get_environment_specific_dawson_url

logger = logging.getLogger(__name__)


class DawsonHowToEfilePetitionPageInitializer(PageInitializer):
    SLUG = "dawson-how-to-e-file-a-petition"
    TITLE = "How to e-file a Petition"
    SCRIPT_NAME = "WAG-1451: Populate How to e-file a Petition User Guide"
    BREADCRUMB_TITLE = "DAWSON User Guides & Electronic Filing Instructions"

    DOCUMENT_FILENAMES = {
        "corporate_disclosure": "Corporate_Disclosure_Statement_Form.pdf",
        "petition": "Petition_Simplified_Form_2.pdf",
        "stin": "Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
        "fee_waiver": "Application_for_Waiver_of_Filing_Fee.pdf",
        "training_guide": "DAWSON_Petitioner_Training_Guide.pdf",
        "training_video": "GMT20201013-122947_Jessica-Ma_1600x900.mp4",
    }

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def get_page_url(self, slug):
        page = Page.objects.filter(slug=slug).first()
        return page.url if page else f"/{slug}/"

    def get_document_url(self, filename):
        document = Document.objects.filter(title=filename).first()
        if document is None:
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=filename,
                title=filename,
            )
        return document.url

    @staticmethod
    def _resource_link(title, url):
        return f'<p><a href="{url}">{title}</a></p>'

    @staticmethod
    def _faq(question, answer, faq_url):
        return {
            "icon": "help",
            "information": f"<p>{question}</p>",
            "information_subtext": (
                f'<p>{answer} View <a href="{faq_url}">full FAQ</a> for more details.</p>'
            ),
        }

    @staticmethod
    def _task(text, subtext=""):
        return {
            "text": f"<p>{text}</p>",
            "subtext": f"<p>{subtext}</p>" if subtext else "",
        }

    def build_timeline(self):
        document_urls = {
            key: self.get_document_url(filename)
            for key, filename in self.DOCUMENT_FILENAMES.items()
        }
        page_urls = {
            "dawson": get_environment_specific_dawson_url(),
            "faq": self.get_page_url("petitioners-help"),
            "filing_checklist": self.get_page_url("petitioners-prepare-to-file"),
            "rules": self.get_page_url("rules"),
            "fees": self.get_page_url("fees-and-charges"),
            "user_guides": self.get_page_url("dawson-user-guides"),
        }
        faq_url = page_urls["faq"]
        guide_pdf_link = self._resource_link(
            "DAWSON Electronic Filing Instructions PDF",
            document_urls["training_guide"],
        )
        dawson_link = self._resource_link("DAWSON", page_urls["dawson"])

        phases = [
            {
                "type": "phase",
                "value": {
                    "title": "Gather Your Information and Documents",
                    "instructions": (
                        "<p>Before starting your case in DAWSON, have the following ready:</p>"
                        "<ul>"
                        "<li>Your IRS notice(s)</li>"
                        "<li>Information needed to identify your case, such as the tax year(s) involved</li>"
                        "<li>Your taxpayer identification information for completing the Statement of Taxpayer Identification Number (STIN)</li>"
                        "<li>A completed Corporate Disclosure Statement (Form 6), if filing on behalf of a corporation, partnership, or LLC</li>"
                        "</ul>"
                    ),
                    "your_tasks": [
                        self._task(
                            "Review the filing deadline on your IRS notice.",
                            "Find the last date to file listed on your IRS notice.",
                        ),
                        self._task(
                            "Make sure you can submit your Petition before the filing deadline.",
                            "In most cases, your Petition must be received by the Court by 11:59 p.m. Eastern Time on the filing deadline.",
                        ),
                        self._task(
                            "Gather the documents you will need before beginning the filing process.",
                            "Preparing your documents in advance can make filing your case faster and easier.",
                        ),
                        self._task(
                            "Decide how you will prepare your Petition.",
                            "Choose whether to use the Petition Generator, the Court's standard form, or your own Petition.",
                        ),
                        self._task(
                            "Review your Petition to ensure it meets filing requirements if uploading your own.",
                            "Remove prohibited information and confirm your Petition meets Court filing requirements before uploading.",
                        ),
                    ],
                    "helpful_information": [
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Corporate Disclosure Statement (Form 6)",
                                document_urls["corporate_disclosure"],
                            ),
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Tax Court Rules of Practice and Procedure",
                                page_urls["rules"],
                            ),
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": dawson_link,
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Filing Checklist – Pro Se",
                                page_urls["filing_checklist"],
                            ),
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "DAWSON Electronic Filing Instructions",
                                page_urls["user_guides"],
                            ),
                            "information_subtext": "",
                        },
                        self._faq(
                            "When should I file my petition?",
                            "In most cases, the Court must receive your petition by 11:59 p.m. Eastern time on the last date to file.",
                            faq_url,
                        ),
                        self._faq(
                            "What information should I remove from documents before filing?",
                            "Remove confidential information before filing, including taxpayer identification information and other protected personal information.",
                            faq_url,
                        ),
                        self._faq(
                            "What documents should not be attached to my petition?",
                            "Do not attach tax returns, receipts, or other evidence to your petition.",
                            faq_url,
                        ),
                    ],
                },
            },
            {
                "type": "phase",
                "value": {
                    "title": "Create a DAWSON Account",
                    "instructions": (
                        "<p>To file electronically, create a DAWSON account.</p>"
                        "<ol><li>Go to DAWSON.</li>"
                        "<li>Select <strong>Create Account</strong>.</li>"
                        "<li>Follow the prompts to create your account.</li></ol>"
                    ),
                    "your_tasks": [
                        self._task(
                            "Determine whether you are filing on behalf of a corporation, partnership, or LLC.",
                            "Business entities are required to submit additional disclosure information when commencing a case.",
                        ),
                        self._task(
                            "If applicable, complete the Corporate Disclosure Statement (Form 6).",
                            "A Corporate Disclosure Statement is required for corporations, partnerships, and LLCs filing a Petition with the Court.",
                        ),
                        self._task(
                            "Save the completed form so it is ready to upload.",
                            "Prepare the completed form for submission during the Create a Case process in DAWSON.",
                        ),
                    ],
                    "helpful_information": [
                        {
                            "icon": "outbound",
                            "information": dawson_link,
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": guide_pdf_link,
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "DAWSON Training Video for Petitioners",
                                document_urls["training_video"],
                            ),
                            "information_subtext": "",
                        },
                        self._faq(
                            "What is DAWSON?",
                            "DAWSON is the U.S. Tax Court's online case management system. You can start a case, file documents, view case information, and manage your case online.",
                            faq_url,
                        ),
                        self._faq(
                            "Do I need a DAWSON account?",
                            "Yes, if you want to file your petition electronically. A DAWSON account also allows you to view your case online and receive Court documents electronically.",
                            faq_url,
                        ),
                    ],
                },
            },
            {
                "type": "phase",
                "value": {
                    "title": "Start Your Case and File Your Petition",
                    "instructions": (
                        "<p>After signing in to DAWSON:</p>"
                        "<ol><li>Select Create a Case.</li>"
                        "<li>Follow the prompts to enter your information.</li>"
                        "<li>Choose how you want to prepare your petition:"
                        "<ol type='a'><li>Enter information and have DAWSON generate your petition, or</li>"
                        "<li>Upload a completed petition.</li></ol></li>"
                        "<li>Upload your IRS notice(s).</li>"
                        "<li>Complete and upload the STIN (Form 4).</li>"
                        "<li>Upload Form 6, if applicable.</li>"
                        "<li>Review and submit your filing.</li></ol>"
                    ),
                    "your_tasks": [],
                    "helpful_information": [
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Petition Form (T.C. Form 2)", document_urls["petition"]
                            ),
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Statement of Taxpayer Identification Number (Form 4)",
                                document_urls["stin"],
                            ),
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": guide_pdf_link,
                            "information_subtext": "",
                        },
                        self._faq(
                            "What is the STIN form?",
                            "The Statement of Taxpayer Identification Number (Form 4) provides identifying information to the Court and IRS and is not part of the public case record.",
                            faq_url,
                        ),
                        self._faq(
                            "Do I need a Corporate Disclosure Statement?",
                            "Yes, if you are filing on behalf of a corporation, partnership, or LLC.",
                            faq_url,
                        ),
                    ],
                },
            },
            {
                "type": "phase",
                "value": {
                    "title": "Receive Your Docket Number and Pay the Filing Fee",
                    "instructions": (
                        "<p>Once your petition is submitted, the Court will assign a docket number.</p>"
                        "<p>Use the docket number to pay the <strong>$60 Petition Filing Fee</strong> through Pay.gov or follow the instructions for mailing payment. Save your docket number and payment confirmation for your records.</p>"
                    ),
                    "your_tasks": [
                        self._task(
                            "Download the Statement of Taxpayer Identification Number (Form 4).",
                            "The STIN helps the IRS identify you and is not visible as part of the case record.",
                        ),
                        self._task(
                            "Complete and save the form so it is ready to upload.",
                            "This is the only document that should contain your Social Security Number (SSN), Taxpayer Identification Number (TIN), or Employer Identification Number (EIN).",
                        ),
                    ],
                    "helpful_information": [
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Court Fees", page_urls["fees"]
                            ),
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": self._resource_link(
                                "Application for Waiver of Filing Fee",
                                document_urls["fee_waiver"],
                            ),
                            "information_subtext": "",
                        },
                        self._faq(
                            "How much does it cost to file a petition?",
                            "The petition filing fee is $60.",
                            faq_url,
                        ),
                        self._faq(
                            "How do I pay the filing fee?",
                            "After your case receives a docket number, use that docket number to pay through Pay.gov.",
                            faq_url,
                        ),
                        self._faq(
                            "What if I cannot afford the filing fee?",
                            "You may request a waiver by filing an Application for Waiver of Filing Fee.",
                            faq_url,
                        ),
                    ],
                },
            },
            {
                "type": "phase",
                "value": {
                    "title": "Manage Your Case in DAWSON",
                    "instructions": (
                        "<p>After filing, use DAWSON to:</p>"
                        "<ul><li>View case activity and documents</li>"
                        "<li>Receive Court documents electronically</li>"
                        "<li>Update your contact information</li>"
                        "<li>File additional documents when required</li></ul>"
                    ),
                    "your_tasks": [
                        self._task(
                            "Create a DAWSON account.",
                            "You must have a DAWSON account before you can electronically file a Petition with the Court.",
                        ),
                        self._task(
                            "Verify that you can successfully access your account.",
                            "After your account is created, you will use it to start a case, file documents, and manage your case online.",
                        ),
                    ],
                    "helpful_information": [
                        {
                            "icon": "outbound",
                            "information": dawson_link,
                            "information_subtext": "",
                        },
                        {
                            "icon": "outbound",
                            "information": guide_pdf_link,
                            "information_subtext": "",
                        },
                        self._faq(
                            "What happens after I file my petition?",
                            "The Court opens your case, assigns a docket number, and the IRS will later file an Answer. You can monitor case activity in DAWSON.",
                            faq_url,
                        ),
                        self._faq(
                            "How do I check the status of my case?",
                            "You can search for your case in DAWSON using your docket number or party name.",
                            faq_url,
                        ),
                        self._faq(
                            "How do I update my contact information?",
                            "Update your email through My Account and update mailing address or phone information within each case.",
                            faq_url,
                        ),
                        self._faq(
                            "How do I file documents after my case is opened?",
                            "Log in to DAWSON and file documents electronically through your case docket.",
                            faq_url,
                        ),
                    ],
                },
            },
        ]

        return {
            "title": self.TITLE,
            "show_title": False,
            "introduction": (
                "<p>Before starting the e-filing process, review the information below. "
                "These instructions explain what is needed and how to file your petition "
                "electronically in DAWSON, the Court's electronic filing and case "
                "management system. In most cases, the Court must receive your "
                "electronically filed petition no later than 11:59 p.m. Eastern time on "
                "the last date to file. Petitions received after this time may be "
                "untimely, and your case may be dismissed.</p>"
            ),
            "show_numbers_in_bubbles": True,
            "warning_callout": {
                "heading": "Important Reminder",
                "text": (
                    "<p>A petition should only be filed once. Filing both electronically "
                    "and by mail may create delays or confusion in processing your case. "
                    "If you already mailed your petition, do not file it again in DAWSON.</p>"
                ),
            },
            "phases": phases,
        }

    def create_page_info(self, home_page):
        user_guides_page = Page.objects.filter(slug="dawson-user-guides").first()
        if user_guides_page is None:
            raise Page.DoesNotExist(
                "Create the DAWSON User Guides landing page before this user guide."
            )

        fields = {
            "seo_title": self.TITLE,
            "search_description": self.TITLE,
            "navigation_ribbon": None,
            "show_floating_definitions_button": True,
            "introductory_text": "",
            "breadcrumb": [
                {
                    "type": "breadcrumb",
                    "value": {
                        "breadcrumb_title": self.BREADCRUMB_TITLE,
                        "breadcrumb_page": [
                            {"type": "internal_page", "value": user_guides_page.id}
                        ],
                    },
                }
            ],
            "body": [{"type": "detailed_timeline", "value": self.build_timeline()}],
        }

        existing_page = Page.objects.filter(slug=self.SLUG).first()
        if existing_page:
            page = existing_page.specific
            if not isinstance(page, PetitionerExperiencePage):
                raise TypeError(
                    f"Page '{self.SLUG}' must be a Petitioner Experience page."
                )
            for field_name, value in fields.items():
                setattr(page, field_name, value)
            action = "Updated"
        else:
            page = home_page.add_child(
                instance=PetitionerExperiencePage(
                    title=self.TITLE,
                    slug=self.SLUG,
                    **fields,
                )
            )
            action = "Created"

        page.title = self.TITLE
        page.save_revision().publish()
        logger.info("%s the '%s' page.", action, self.TITLE)

    def run(self):
        if ExecuteScript.command_exists(self.SCRIPT_NAME):
            logger.info("Script '%s' already exists. Skipping.", self.SCRIPT_NAME)
            return 0

        script_entry = ExecuteScript.create_script(self.SCRIPT_NAME)
        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = (
                "DAWSON How to e-file a Petition page created or updated successfully."
            )
            script_entry.save()
        except Exception as error:
            logger.exception("Could not initialize the DAWSON e-file petition page.")
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error}"
            script_entry.save()
            raise
