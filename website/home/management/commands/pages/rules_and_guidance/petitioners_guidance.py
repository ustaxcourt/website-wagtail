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
computer_icon_name = "computer_icon.svg"
mail_icon_name = "mail.svg"


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
        _petitioner_timeline_url = urljoin(_base_url, "/petitioners-timeline")

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

        computer_doc = Document.objects.filter(title=computer_icon_name).first()
        if computer_doc:
            logger.info("'Computer Icon' icon already exists.")
        else:
            logger.info("Creating the 'Computer Icon' icon.")
            computer_doc = self.load_document_from_documents_dir(
                subdirectory=None,
                filename="computer_icon.svg",
                title="Computer Icon",
            )

        mail_doc = Document.objects.filter(title=mail_icon_name).first()
        if mail_doc:
            logger.info("'Mail Icon' icon already exists.")
        else:
            logger.info("Creating the 'Mail Icon' icon.")
            mail_doc = self.load_document_from_documents_dir(
                subdirectory=None,
                filename="mail.svg",
                title="Mail Icon",
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
                            "callout_block": [
                                {
                                    "type": "block",
                                    "value": {
                                        "heading": "Deadline for Filing:",
                                        "text": '<p data-block-key="mgzeg">A document filed through DAWSON is timely if it is electronically filed by 11:59 p.m., Eastern time, on the day it is due.</p>',
                                        "callout_type": "info",
                                    },
                                    "id": "452cb185-bc8e-40e7-a422-ecb9a83925e6",
                                }
                            ],
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
                        "id": "5e5c3858-b562-4818-9b68-169833009415",
                    },
                    {
                        "type": "paragraph",
                        "value": f'<h2 data-block-key="cuzcn"><b>Get Started</b> <a href= {_petitioner_timeline_url}>(View detailed timeline)</a></h2>',
                        "id": "2ba9f031-2068-41b9-afba-0fc25ce8c052",
                    },
                    {
                        "type": "card",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "fa-solid fa-1",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": None,
                                    "title_icon_alt_text": "",
                                    "subtitle": "",
                                    "title": "File Your Petition (DAWSON)",
                                    "description": '<p data-block-key="j716r">Securely file your petition using the online generator or upload your completed PDF.</p>',
                                    "buttons": [],
                                },
                                "id": "bf1f6c20-d383-4046-bddd-8d671e964f61",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "fa-solid fa-2",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": None,
                                    "title_icon_alt_text": "",
                                    "subtitle": "",
                                    "title": "Receive Confirmation",
                                    "description": '<p data-block-key="j716r">Instantly receive your official Docket Number and a printable electronic receipt confirming your filing.</p>',
                                    "buttons": [],
                                },
                                "id": "cf8b7b1c-d8cc-40e3-9fd6-62177ab7f8c2",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "fa-solid fa-3",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": None,
                                    "title_icon_alt_text": "",
                                    "subtitle": "",
                                    "title": "Pay Filing Fee (Pay.gov)",
                                    "description": '<p data-block-key="j716r">Pay the required $60 filing fee through the secure federal payment gateway, or request a fee waiver if you qualify.</p>',
                                    "buttons": [],
                                },
                                "id": "b391b8f5-0a6b-4c32-9dc7-444aee575d74",
                            },
                        ],
                        "id": "8a6d6de4-b347-40c5-9f95-792200a223ab",
                    },
                    {
                        "type": "icon_header",
                        "value": {"icon": "fa-solid fa-file", "text": "How to File"},
                        "id": "346218f7-ec8e-47e0-a60d-6696f90e4d8f",
                    },
                    {
                        "type": "card",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "color": "dark-primary",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": computer_doc.pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "",
                                    "title": "Electronic Filing - Recommended",
                                    "description": '<ul><li data-block-key="2lysw">File your petition electronically using DAWSON</li><li data-block-key="3rclc">Use the petition generator in DAWSON or upload a PDF (<a linktype="document" id="505">Petition Form</a>)</li><li data-block-key="909he">Immediate confirmation of filing</li></ul><p data-block-key="9e3d3">Visit <a href="https://dawson.ustaxcourt.gov">dawson.ustaxcourt.gov</a> to get started.</p>',
                                    "buttons": [],
                                },
                                "id": "6623707a-b1e6-4894-85d9-a983996ff861",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "dark-primary",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": mail_doc.pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "",
                                    "title": "Can't file electronically? Mail Your Petition",
                                    "description": '<ul><li data-block-key="2lysw">Download the Petition Kit</li><li data-block-key="3rclc">Complete all the forms</li><li data-block-key="909he">Mail all forms to the US Tax Court</li></ul><p data-block-key="9e3d3">Mail to: <a href="https://www.google.com/maps/place/US+Tax+Court/@38.895172,-77.0175094,17z/data=!3m1!4b1!4m6!3m5!1s0x89b7b788e9a932e5:0x33d2d11766456bca!8m2!3d38.8951679!4d-77.0149345!16zL20vMDVzZDE0?entry=ttu&amp;g_ep=EgoyMDI2MDkxNi4wIKXMDSoASAFQAw%3D%3D">United States Tax Court, 400 Second St. NW Washington, DC 20217</a></p>',
                                    "buttons": [],
                                },
                                "id": "a2afe469-e55c-4aa4-9a06-eaaec3ef5cc2",
                            },
                        ],
                        "id": "562bdadf-fd26-457f-9d22-47b1f810d6ed",
                    },
                    {
                        "type": "callout",
                        "value": {
                            "heading": "NOTE FOR PETITIONERS WHO FILE BY MAIL:",
                            "text": '<p data-block-key="b64or">Petitioners who file by mail cannot immediately switch to electronic access. To protect your information, the United States Tax Court will mail identity verification instructions to your address of record. Switching to electronic access will be available only after the verification process is complete. Consider filing electronically from the start to get electronic access to your case immediately.</p>',
                            "callout_type": "warning",
                        },
                        "id": "b9361c22-d50d-448b-8350-14bf5807fd5f",
                    },
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
