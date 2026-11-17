from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
import logging
import uuid
from home.models.utils.execute_script import ExecuteScript
from home.models.pages.petitioner_experience import PetitionerExperiencePage


logger = logging.getLogger(__name__)

PAGE_SLUG = "dawson-troubleshoot-file-uploads"
CREATE_COMMAND_NAME = "WAG-1450: How to troubleshoot file upload errors"
RESOURCES_COMMAND_NAME = (
    "WAG-1484: Add resource cards to How to troubleshoot file upload errors"
)
HIDE_TITLE_COMMAND_NAME = (
    "WAG-1484: Hide duplicate timeline title on How to troubleshoot file upload errors"
)
PDF_ICON_FILENAME = "PDF_icon.svg"

# (title, link) for the Resources column, in display order.
troubleshoot_file_uploads_resources = [
    (
        "Adobe Convert files to PDFs User Guide",
        "https://helpx.adobe.com/acrobat/desktop/create-documents/create-pdfs/convert-to-pdf.html",
    ),
    (
        "Adobe Combine files into one PDF User Guide",
        "https://helpx.adobe.com/acrobat/desktop/edit-documents/combine-files/combine-files.html",
    ),
    (
        "Adobe Remove passwords from PDF User Guide",
        "https://helpx.adobe.com/acrobat/desktop/protect-documents/protect-with-passwords/remove-passwords-from-pdfs.html",
    ),
]

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


def _options(
    summary, options, lead="Try one of the following options to resolve the issue:"
):
    items = "".join(f"<li>{option}</li>" for option in options)
    return f"<p>{summary}</p><p>{lead}</p><ul>{items}</ul>"


def _phase(title, instructions, helpful_information=(), show_info_icon=False):
    return {
        "type": "phase",
        "value": {
            "title": title,
            "date_range": "",
            "show_info_icon": show_info_icon,
            "instructions": instructions,
            "your_tasks": [],
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


class DawsonTroubleshootFileUploads(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def build_resource_cards(self):
        icon = self.load_document_from_documents_dir(
            subdirectory=None,
            filename=PDF_ICON_FILENAME,
            title=PDF_ICON_FILENAME,
        )
        return [
            {
                "type": "quick_access_tiles",
                "value": {
                    "tiles_hover_enabled": True,
                    "icon_position": "desktop_top_mobile_left",
                    "tiles": [
                        {
                            "type": "item",
                            "value": {
                                "title": title,
                                "description": "",
                                "icon": {"svg_file": icon.pk},
                                "content_alignment": "left",
                                "link": [
                                    {
                                        "type": "external_url",
                                        "value": url,
                                        "id": str(uuid.uuid4()),
                                    }
                                ],
                            },
                            "id": str(uuid.uuid4()),
                        }
                        for title, url in troubleshoot_file_uploads_resources
                    ],
                },
                "id": str(uuid.uuid4()),
            }
        ]

    def hide_timeline_title(self):
        """The page heading already shows the title, so hide the timeline's copy."""
        page = PetitionerExperiencePage.objects.filter(slug=PAGE_SLUG).first()
        if page is None:
            logger.warning(f"Page '{PAGE_SLUG}' not found; timeline title unchanged.")
            return

        body = page.body.get_prep_value()
        changed = False
        for block in body:
            if block["type"] == "detailed_timeline" and block["value"].get(
                "show_title", True
            ):
                block["value"]["show_title"] = False
                changed = True
        if not changed:
            return

        page.body = body
        page.save_revision().publish()

    def add_resource_cards(self):
        """Adds the Resources column to a page created before it existed."""
        page = PetitionerExperiencePage.objects.filter(slug=PAGE_SLUG).first()
        if page is None:
            logger.warning(f"Page '{PAGE_SLUG}' not found; no resource cards added.")
            return
        if page.resource_cards:
            logger.info(f"Page '{PAGE_SLUG}' already has resource cards.")
            return

        page.resource_cards = self.build_resource_cards()
        page.save_revision().publish()

    def create_page_info(self, home_page):
        slug = PAGE_SLUG
        title = "How to troubleshoot file upload errors"

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
                search_description=title,
                breadcrumb=breadcrumb,
                show_floating_definitions_button=True,
                resource_cards=self.build_resource_cards(),
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
                            "show_title": False,
                            "show_numbers_in_bubbles": True,
                            "phases": [
                                _phase(
                                    "Error Message #1: File size too big",
                                    _options(
                                        "DAWSON could not upload the document because the file "
                                        "exceeds the maximum upload size limit.",
                                        [
                                            "Check the size of the document you are uploading. "
                                            "Documents uploaded to DAWSON must be 250 MB or less.",
                                            "If a document exceeds 250 MB, divide it into multiple "
                                            "files before uploading.",
                                        ],
                                    ),
                                ),
                                _phase(
                                    "Error Message #2: The file is corrupt or in an unsupported PDF format",
                                    _options(
                                        "DAWSON cannot process PDF files that are damaged, improperly "
                                        "created, or saved in an unsupported format. Creating a new PDF "
                                        "often resolves these issues.",
                                        [
                                            "Re-save the file and confirm it opens properly in Adobe "
                                            "Acrobat. Verify that the PDF opens without error before "
                                            "uploading it again.",
                                            "Save the document using Print to PDF. Creating a new PDF "
                                            "may resolve formatting or compatibility issues.",
                                            "Print the document and scan it as a new PDF. A newly "
                                            "scanned PDF may upload successfully if the original file "
                                            "is damaged or unsupported.",
                                        ],
                                    ),
                                ),
                                _phase(
                                    "Error Message #3: Your firewall or network may be preventing submission",
                                    _options(
                                        "DAWSON could not complete the upload because a network or "
                                        "firewall setting may be blocking the connection.",
                                        [
                                            "Try uploading the document using a different network or "
                                            "Wi-Fi connection. Testing another network can help "
                                            "determine whether your current network is blocking the "
                                            "upload.",
                                            "If the upload succeeds on another network, the issue may "
                                            "be caused by a network or firewall restriction.",
                                            "If necessary, contact your network administrator. They "
                                            "may need to adjust firewall settings to allow document "
                                            "submissions to DAWSON.",
                                        ],
                                    ),
                                ),
                                _phase(
                                    "Error Message #4: There is a problem with this file",
                                    _options(
                                        "DAWSON encountered an issue while processing the uploaded "
                                        "document. This may be related to the file itself or the "
                                        "browser being used.",
                                        [
                                            "Verify that your browser is up to date.",
                                            "Install any available browser updates.",
                                            "Try uploading the file again after updating your browser.",
                                        ],
                                    ),
                                    helpful_information=[
                                        (
                                            "What are the technical requirements for accessing DAWSON?",
                                            "To use DAWSON, you only need an internet connection and a "
                                            "current web browser. DAWSON works with Chrome, Microsoft "
                                            "Edge, Firefox, and Safari. You do not need to install any "
                                            "software.",
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
                                    f"{images['dawson_faqs_case_management_secured.jpg']}<hr/>"
                                    '<p><b>If you see "(SECURED)" at the top of the document</b></p>'
                                    "<p>Create a new document file, and when signing it, decline "
                                    'Adobe\'s prompt to save a read-only copy by clicking "Cancel" on '
                                    "the screen when prompted. This will prevent Adobe from "
                                    "automatically applying security measures to the file.</p>"
                                    f"{images['dawson_faqs_case_management_banner.jpg']}<hr/>"
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
                                    _options(
                                        "If the upload continues to fail after following the "
                                        "recommended troubleshooting steps, additional assistance "
                                        "may be required.",
                                        [
                                            "Review the troubleshooting steps for your specific error "
                                            "message.",
                                            "Most upload issues can be resolved by correcting file, "
                                            "browser, network, or security settings.",
                                            "Attempt the upload again after making the recommended "
                                            "changes.",
                                            "Contact DAWSON Support if the issue continues after "
                                            "troubleshooting.",
                                        ],
                                        lead="Consider the following options:",
                                    ),
                                    show_info_icon=True,
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
        """Create the Dawson How to troubleshoot file upload errors page and its resource cards"""
        created = self._run_once(CREATE_COMMAND_NAME, self.create, self._check_parent)
        updated = self._run_once(RESOURCES_COMMAND_NAME, self.add_resource_cards)
        retitled = self._run_once(HIDE_TITLE_COMMAND_NAME, self.hide_timeline_title)
        if not (created or updated or retitled):
            return 0

    def _check_parent(self):
        # Check before recording the script so a missing parent page is retried
        # on the next deploy instead of being permanently marked as run.
        if not Page.objects.filter(slug="dawson-user-guides").exists():
            raise Exception(
                f"'dawson-user-guides' page not found; cannot run '{CREATE_COMMAND_NAME}'."
            )

    def _run_once(self, command_name, action, precheck=None):
        """Runs action once per environment; returns False if it already ran."""
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return False

        if precheck:
            precheck()

        script_entry = ExecuteScript.create_script(command_name)

        try:
            action()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = f"{command_name} completed successfully."
            script_entry.save()
        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
        return True
