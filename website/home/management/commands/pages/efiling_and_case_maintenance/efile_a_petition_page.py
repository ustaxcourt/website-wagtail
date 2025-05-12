from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)

efile_a_petition_images = [
    {
        "title": "Start A Case",
        "filename": "start-a-case.jpg",
    },
    {
        "title": "Create A Case Process",
        "filename": "create-a-case-process.jpg",
    },
    {
        "title": "Petition Submitted",
        "filename": "petition-submitted.jpg",
    },
]

efile_a_petition_docs = {
    "Petition_Simplified_Form_2.pdf": "",
    "Corporate_Disclosure_Statement_Form.pdf": "",
    "Form_4_Statement_of_Taxpayer_Identification_Number.pdf": "",
}


class EfileAPetitionPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "efile-a-petition"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "How to eFile a Petition"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in efile_a_petition_images:
            image_uploaded = self.load_image_from_images_dir(
                "dawson", image["filename"], image["title"]
            )

            if image_uploaded:
                uploaded_images[image["filename"]] = {
                    "id": image_uploaded.id,
                    "url": image_uploaded.file.url,
                }

        for doc_name in efile_a_petition_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            efile_a_petition_docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": """Before starting the e-filing process, please review the helpful tips provided below. They will instruct you in what is needed and how to go about filing your petition electronically in DAWSON (Docket Access Within and Secure Online Network), the Court’s electronic filing and case management system. For more detailed instructions, refer to the <a href="/dawson-user-guides" title="DAWSON User Guides">DAWSON user guides</a>.""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Check the Deadline for Filing",
                    },
                    {
                        "type": "paragraph",
                        "value": "You may have received a notice in the mail from the Internal Revenue Service (IRS). <strong>In most cases, the Court must receive your electronically filed Petition no later than 11:59 pm Eastern Time on the last date to file</strong>. Petitions received after this time may be untimely and your case may be dismissed.",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Before You Electronically File a Petition",
                    },
                    {
                        "type": "paragraph",
                        "value": "Before starting a case and filing a Petition with the Court, you can prepare forms and documents in advance.  After the petition has been processed, you'll be able to log in at any time to view the status and take action in the case ",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": "Complete the Petition",
                                    "nested_list": [
                                        {
                                            "list_type": "ordered",
                                            "items": [
                                                {
                                                    "text": "This is the document that explains why you disagree with the Internal Revenue Service (IRS). There are three methods to file the Petition:",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "ordered",
                                                            "items": [
                                                                {
                                                                    "text": "Answer some questions online and have DAWSON create a Petition document for filing with the Court.",
                                                                },
                                                                {
                                                                    "text": (
                                                                        "Complete and upload the Court's standard Petition form. "
                                                                        f"<a href=\"{efile_a_petition_docs['Petition_Simplified_Form_2.pdf'].file.url}\" "
                                                                        "target=\"_blank\" title=\"Petition\">Petition form (T.C. Form 2)</a>"
                                                                    ),
                                                                },
                                                                {
                                                                    "text": """Upload your own Petition that complies with the requirements of the <a href="/rules" title="Tax Court Rules">Tax Court Rules of Practice and Procedure</a>.""",
                                                                },
                                                            ],
                                                        }
                                                    ],
                                                },
                                                {
                                                    "text": "If you choose to upload a Petition:",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "ordered",
                                                            "items": [
                                                                {
                                                                    "text": "Do <strong>NOT</strong> put your Social Security number, Taxpayer ID number, or Employee ID number on the Petition.",
                                                                },
                                                                {
                                                                    "text": "Do <strong>NOT</strong> attach any other documents (such as tax returns, copies of receipts, or other types of evidence) to your Petition.",
                                                                },
                                                                {
                                                                    "text": "Do <strong>NOT</strong> include names of minor children or financial account numbers.",
                                                                },
                                                            ],
                                                        }
                                                    ],
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "text": (
                                        "If you are filing on behalf of a business (this includes a corporation, partnership, or LLC), "
                                        f"<a href=\"{efile_a_petition_docs['Corporate_Disclosure_Statement_Form.pdf'].file.url}\" "
                                        "target=\"_blank\" title=\"Corporate Disclosure Statement Form\">Corporate Disclosure Statement</a> (Form 6)."
                                    ),
                                },
                                {
                                    "text": "Upload IRS Notice(s)",
                                    "nested_list": [
                                        {
                                            "list_type": "ordered",
                                            "items": [
                                                {
                                                    "text": "If you received one or more Notices from the IRS:",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "ordered",
                                                            "items": [
                                                                {
                                                                    "text": "You will be asked to upload a PDF of the Notice(s) if you received one.",
                                                                },
                                                                {
                                                                    "text": "Remove or block out (redact) Social Security Numbers (SSN), Taxpayer Identification Numbers (TIN), or Employer Identification Numbers (EIN) on a COPY of the IRS Notice(s) or in a manner that does not permanently alter the original IRS Notice(s).",
                                                                },
                                                                {
                                                                    "text": "The Notice(s) will be part of the case record.",
                                                                },
                                                            ],
                                                        }
                                                    ],
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "text": "Confirm your identity",
                                    "nested_list": [
                                        {
                                            "list_type": "ordered",
                                            "items": [
                                                {
                                                    "text": """You'll be asked to complete and upload a Statement of Taxpayer Identification Number (STIN) form. This document is sent to the IRS to help them identify you, but it's never visible as part of the case record. <strong>This is the only document that should contain your Social Security Number (SSN), Taxpayer Identification Number (TIN), or Employee Identification Number (EIN)</strong>.""",
                                                },
                                                {
                                                    "text": (
                                                        "Download and complete the Statement of Taxpayer Identification Number. "
                                                        f"<a href=\"{efile_a_petition_docs['Form_4_Statement_of_Taxpayer_Identification_Number.pdf'].file.url}\" "
                                                        "target=\"_blank\" title=\"Statement of Taxpayer Identification Number\">Download the form</a> and fill it out to submit it."
                                                    ),
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "text": "Pay the $60 filing fee",
                                    "nested_list": [
                                        {
                                            "list_type": "ordered",
                                            "items": [
                                                {
                                                    "text": "After you submit your case, you'll be asked to pay a $60 filing fee.",
                                                },
                                                {
                                                    "text": "You may pay online or mail a check/money order.",
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "text": "<strong>File once. Do NOT file a Petition both electronically and by mail.</strong>",
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "File a Petition Electronically in DAWSON",
                    },
                    {
                        "type": "paragraph",
                        "value": """<strong>Create a DAWSON Account</strong>
                                    <br>
                                    <br>
                                    If you have not yet set up a DAWSON account, create a new account.
                                    """,
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": """Go to <a href="https://dawson.ustaxcourt.gov" target="_blank" title="DAWSON">DAWSON</a>.""",
                                },
                                {
                                    "text": "Click Log In at the top right.",
                                },
                                {
                                    "text": "Click Sign Up at the bottom of the login screen.",
                                },
                                {
                                    "text": "Follow the prompts.",
                                },
                                {
                                    "text": """For more detailed instructions on creating a new account, refer to the <a href="/dawson-user-guides" title="DAWSON User Guides">DAWSON user guides</a>.""",
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Start a Case",
                    },
                    {
                        "type": "paragraph",
                        "value": "Once you have created your account, you can file the petition electronically in DAWSON.",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": "Review the information provided in the <strong>What to Expect When Filing a Case Online</strong> section.",
                                },
                                {
                                    "text": "Select the Start a Case button at the bottom of the page.",
                                    "image": uploaded_images["start-a-case.jpg"]["id"],
                                },
                                {
                                    "text": "Follow the prompts. There will be 7 steps to complete the Create a Case Process. All fields are required unless noted as optional.",
                                    "image": uploaded_images[
                                        "create-a-case-process.jpg"
                                    ]["id"],
                                },
                                {
                                    "text": "Once your Petition is submitted, you will be assigned a Docket Number and given some information about what to expect next.",
                                    "image": uploaded_images["petition-submitted.jpg"][
                                        "id"
                                    ],
                                },
                                {
                                    "text": """For more detailed information on filing a Petition electronically, refer to the <a href="/dawson-user-guides"  title="DAWSON User Guides">DAWSON user guides</a>.""",
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Electronically File Documents and Other Actions in DAWSON",
                    },
                    {
                        "type": "paragraph",
                        "value": """You will be able to log in to DAWSON at any time and view your case. In addition, you can file other documents, update your contact information, and view documents in your case that are filed by the Court or other parties. Refer to the <a href="/dawson-user-guides" title="DAWSON User Guides">DAWSON user guides</a> for more detailed instructions.""",
                    },
                ],
                search_description="Learn how to eFile a Petition",
            )
        )

        new_page.save_revision().publish()
        logger.info(f"Successfully created the '{title}' page.")
