from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
import logging
import uuid
from home.models.utils.execute_script import ExecuteScript
from home.models.pages.petitioner_experience import PetitionerExperiencePage


logger = logging.getLogger(__name__)

# Same images (and titles) as the DAWSON FAQs page, so existing uploads are reused.
troubleshoot_file_uploads_images = [
    {
        "title": "image of the Dawson faqs case management secured",
        "filename": "dawson_faqs_case_management_secured.jpg",
        "alt": "A PDF open in Adobe with a blue banner and (SECURED) shown at the top of the document",
    },
    {
        "title": "image of the Dawson faqs case management banner",
        "filename": "dawson_faqs_case_management_banner.jpg",
        "alt": "Adobe prompt to save a read-only copy of a signed document",
    },
    {
        "title": "image of the Dawson faqs case management document properties",
        "filename": "dawson_faqs_case_management_properties.jpg",
        "alt": "Adobe Document Properties Security tab with Security Method set to No Security",
    },
]


def _phase(title, instructions, your_tasks=(), helpful_information=()):
    return {
        "type": "phase",
        "value": {
            "title": title,
            "date_range": "",
            "instructions": instructions,
            "your_tasks": [
                {
                    "type": "item",
                    "value": {"text": f"<p>{text}</p>", "subtext": f"<p>{subtext}</p>"},
                    "id": str(uuid.uuid4()),
                }
                for text, subtext in your_tasks
            ],
            "helpful_information": [
                {
                    "type": "item",
                    "value": {
                        "icon": "help",
                        "information": f"<p>{information}</p>",
                        "information_subtext": f"<p>{subtext}</p>",
                    },
                    "id": str(uuid.uuid4()),
                }
                for information, subtext in helpful_information
            ],
        },
    }


# Shown under both Error Message #2 and #3, as in the design.
_new_pdf_tasks = [
    (
        "Re-save the file and confirm it opens properly in Adobe Acrobat.",
        "Verify that the PDF opens without error before uploading it again.",
    ),
    (
        "Save the document using Print to PDF.",
        "Creating a new PDF may resolve formatting or compatibility issues.",
    ),
    (
        "Print the document and scan it as a new PDF.",
        "A newly scanned PDF may upload successfully if the original file is "
        "damaged or unsupported.",
    ),
]


class DawsonTroubleshootFileUploads(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-troubleshoot-file-uploads"
        title = "How to troubleshoot file upload errors"

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        user_guides_page = Page.objects.get(slug="dawson-user-guides")
        breadcrumb = [
            {
                "type": "breadcrumb",
                "value": {
                    "breadcrumb_title": "DAWSON User Guides & Electronic Filing Instructions",
                    "breadcrumb_page": [
                        {"type": "internal_page", "value": user_guides_page.id}
                    ],
                },
            }
        ]

        images = {}
        for image in troubleshoot_file_uploads_images:
            uploaded = self.load_image_from_images_dir(
                "dawson", image["filename"], image["title"]
            )
            images[image["filename"]] = (
                f'<embed alt="{image["alt"]}" embedtype="image" format="fullwidth" id="{uploaded.id}"/>'
                if uploaded
                else ""
            )

        logger.info(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                breadcrumb=breadcrumb,
                show_floating_definitions_button=True,
                body=[
                    {
                        "type": "detailed_timeline",
                        "value": {
                            "title": title,
                            "introduction": (
                                "<p>If you receive an error while uploading a document in DAWSON, "
                                "the issue is often related to file size, PDF format, browser "
                                "settings, network restrictions, or document security settings.</p>"
                                "<p>Use the steps below to identify and resolve the most common "
                                "upload errors.</p>"
                            ),
                            "show_numbers_in_bubbles": True,
                            "phases": [
                                _phase(
                                    "Error Message #1: File size too big",
                                    "<p>DAWSON could not upload the document because the file "
                                    "exceeds the maximum upload size limit.</p>",
                                    your_tasks=[
                                        (
                                            "Check the size of the document you are uploading.",
                                            "Documents uploaded to DAWSON must be 250 MB or less.",
                                        ),
                                        (
                                            "Split large documents into smaller files, if necessary.",
                                            "If a document exceeds 250 MB, divide it into multiple "
                                            "files before uploading.",
                                        ),
                                    ],
                                ),
                                _phase(
                                    "Error Message #2: The file is corrupt or in an unsupported PDF format",
                                    "<p>DAWSON cannot process PDF files that are damaged, improperly "
                                    "created, or saved in an unsupported format. Creating a new PDF "
                                    "often resolves these issues.</p>",
                                    your_tasks=_new_pdf_tasks,
                                ),
                                _phase(
                                    "Error Message #3: Your firewall or network may be preventing submission",
                                    "<p>DAWSON could not complete the upload because a network or "
                                    "firewall setting may be blocking the connection.</p>",
                                    your_tasks=_new_pdf_tasks,
                                ),
                                _phase(
                                    "Error Message #4: There is a problem with this file",
                                    "<p>DAWSON encountered an issue while processing the uploaded "
                                    "document. This may be related to the file itself or the browser "
                                    "being used.</p>",
                                    your_tasks=[
                                        (
                                            "Download the Statement of Taxpayer Identification Number (Form 4)",
                                            "The STIN helps the IRS identify you and is not visible "
                                            "as part of the case record.",
                                        ),
                                        (
                                            "Complete and save the form so it is ready to upload",
                                            "This is the only document that should contain your "
                                            "Social Security Number (SSN), Taxpayer Identification "
                                            "Number (TIN), or Employer Identification Number (EIN).",
                                        ),
                                    ],
                                    helpful_information=[
                                        (
                                            "What information should I remove from documents before filing?",
                                            "Before filing a document, remove or redact sensitive "
                                            "personal information such as Social Security numbers, "
                                            "dates of birth, names of minor children, and financial "
                                            "account numbers. View "
                                            '<a href="/petitioners-start#START17">full FAQ</a> for more details.',
                                        ),
                                    ],
                                ),
                                _phase(
                                    "Error Message #5: The file is encrypted or password protected",
                                    "<p>If you signed your document electronically using a program "
                                    "such as Adobe Acrobat, the file may have been automatically saved "
                                    "as a read-only or secured document. DAWSON cannot accept encrypted "
                                    "or password-protected PDF files. Review the document for a "
                                    '"(SECURED)" banner or security settings before attempting to '
                                    "upload it again.</p>"
                                    f"{images['dawson_faqs_case_management_secured.jpg']}"
                                    '<p><b>If you see "(SECURED)" at the top of the document</b></p>'
                                    "<p>Create a new document file, and when signing it, decline "
                                    'Adobe\'s prompt to save a read-only copy by clicking "Cancel" on '
                                    "the screen when prompted. This will prevent Adobe from "
                                    "automatically applying security measures to the file.</p>"
                                    f"{images['dawson_faqs_case_management_banner.jpg']}"
                                    '<p><b>If you do not see "(SECURED)" at the top of the document</b></p>'
                                    '<p>If you do NOT see the above banner or "(SECURED)" in the '
                                    "document window, follow these steps.</p>"
                                    "<ol>"
                                    "<li>Right-click in the document.</li>"
                                    "<li>Choose Document Properties from the options.</li>"
                                    "<li>Click on the Security tab.</li>"
                                    '<li>In the dropdown menu labeled Security Method, select "No Security".</li>'
                                    "<li>Click OK.</li>"
                                    "<li>Save the document. You should now be able to upload the "
                                    "document to DAWSON without error.</li>"
                                    "</ol>"
                                    f"{images['dawson_faqs_case_management_properties.jpg']}",
                                    helpful_information=[
                                        (
                                            "What digital signatures are accepted in DAWSON?",
                                            "You may upload documents with a handwritten signature "
                                            "scanned into a PDF, use an electronic signature tool such "
                                            "as Adobe Acrobat or DocuSign, or upload documents "
                                            "containing high-resolution images or digitized signatures. "
                                            "Documents must be uploaded without encryption or password "
                                            "protection. View "
                                            '<a href="/dawson-faqs-case-management#FAQS7">full FAQ</a> for more details.',
                                        ),
                                    ],
                                ),
                                _phase(
                                    "Additional Troubleshooting",
                                    "<p>If the upload continues to fail after following the "
                                    "recommended troubleshooting steps, additional assistance may "
                                    "be required.</p>",
                                    your_tasks=[
                                        (
                                            "Review the troubleshooting steps for your specific error message.",
                                            "Most upload issues are resolved by correcting the file, "
                                            "browser, network, or security settings.",
                                        ),
                                        (
                                            "Attempt the upload again.",
                                            "Retry the upload after making the recommended changes.",
                                        ),
                                        (
                                            "Contact DAWSON Support.",
                                            "Technical support is available if the issue continues "
                                            "after troubleshooting.",
                                        ),
                                    ],
                                    helpful_information=[
                                        (
                                            "How can I access DAWSON and confirm it is working properly?",
                                            "You can access DAWSON from a computer, smartphone, or "
                                            "tablet by visiting "
                                            '<a href="https://dawson.ustaxcourt.gov/">DAWSON</a> '
                                            "directly. To check whether DAWSON is operating normally or "
                                            "to view scheduled maintenance, visit the "
                                            '<a href="https://status.ustaxcourt.gov/">system status page</a>. '
                                            'View <a href="/dawson-faqs-basics#FAQS4">full FAQ</a> for more details.',
                                        ),
                                    ],
                                ),
                            ],
                        },
                    }
                ],
            )
        )

        new_page.save_revision().publish()

    def run(self):
        """Update the Dawson How to troubleshoot file upload errors"""
        command_name = "WAG-1450: How to troubleshoot file upload errors"
        # Check if script already exists
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        # Check before recording the script so a missing parent page is retried
        # on the next deploy instead of being permanently marked as run.
        if not Page.objects.filter(slug="dawson-user-guides").exists():
            raise Exception(
                f"'dawson-user-guides' page not found; cannot run '{command_name}'."
            )

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.create()
            execution_log_text = "Dawson How to troubleshoot file upload errors page updated successfully."
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = execution_log_text
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
