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
GET_STARTED_BLOCK_ID = "2ba9f031-2068-41b9-afba-0fc25ce8c052"
GET_STARTED_CARDS_BLOCK_ID = "8a6d6de4-b347-40c5-9f95-792200a223ab"
HOW_TO_FILE_HEADER_BLOCK_ID = "bc4972ca-503f-466a-9fb0-4b204622d650"
HOW_TO_FILE_CARDS_BLOCK_ID = "5439cbe3-d512-424d-ac65-06d18cd2e3ac"
HOW_TO_FILE_CALLOUT_BLOCK_ID = "037efcb7-c2e8-4847-8d76-f3274ec841bc"
HOW_TO_FILE_BLOCK_IDS = {
    HOW_TO_FILE_HEADER_BLOCK_ID,
    HOW_TO_FILE_CARDS_BLOCK_ID,
    HOW_TO_FILE_CALLOUT_BLOCK_ID,
}


class PetitionersGuidancePageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def build_get_started_block(self, petitioner_timeline_url):
        return {
            "type": "section_header",
            "value": {
                "heading": "Get Started",
                "link_text": "View detailed timeline",
                "link_url": petitioner_timeline_url,
            },
            "id": GET_STARTED_BLOCK_ID,
        }

    def build_how_to_file_blocks(
        self, computer_icon_doc, mail_icon_doc, petition_form_doc, petition_kit_doc
    ):
        return [
            {
                "type": "icon_header",
                "value": {"icon": "draft", "text": "How to File"},
                "id": HOW_TO_FILE_HEADER_BLOCK_ID,
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
                            "title_icon": computer_icon_doc.pk,
                            "title_icon_alt_text": "",
                            "subtitle": "",
                            "title": "Electronic Filing - Recommended",
                            "description": f'<ul><li>File your petition electronically using DAWSON</li><li>Use the petition generator in DAWSON or upload a PDF (<a linktype="document" id="{petition_form_doc.pk}">Petition Form</a>)</li><li>Immediate confirmation of filing</li></ul><p>Visit <strong><a href="https://dawson.ustaxcourt.gov/">dawson.ustaxcourt.gov</a></strong> to get started.</p>',
                            "buttons": [],
                        },
                        "id": "27680fe9-a643-41cf-b4f7-29dd6ed7ccda",
                    },
                    {
                        "type": "item",
                        "value": {
                            "color": "dark-primary",
                            "numbered_icon": "",
                            "numbered_icon_alignment": "left",
                            "title_icon": mail_icon_doc.pk,
                            "title_icon_alt_text": "",
                            "subtitle": "",
                            "title": "Can't file electronically? Mail Your Petition",
                            "description": f'<ul><li>Download the <a linktype="document" id="{petition_kit_doc.pk}">Petition Kit</a></li><li>Complete all the forms</li><li>Mail all forms to the US Tax Court</li></ul><p>Mail to: <a href="https://www.google.com/maps/search/?api=1&amp;query=United+States+Tax+Court%2C+400+Second+Street+NW%2C+Washington%2C+DC+20217">United States Tax Court, 400 Second St. NW Washington, DC 20217</a></p>',
                            "buttons": [],
                        },
                        "id": "8955354d-3c1d-425d-803a-014b572d2709",
                    },
                ],
                "id": HOW_TO_FILE_CARDS_BLOCK_ID,
            },
            {
                "type": "callout",
                "value": {
                    "heading": "NOTE FOR Petitioners who file by mail:",
                    "text": '<p data-block-key="vlez3">Petitioners who file by mail cannot immediately switch to electronic access. To protect your information, the United States Tax Court will mail identity verification instructions to your address of record. Switching to electronic access will be available only after the verification process is complete. Consider filing electronically from the start to get electronic access to your case immediately.</p>',
                    "callout_type": "warning",
                },
                "id": HOW_TO_FILE_CALLOUT_BLOCK_ID,
            },
        ]

    def update_existing_page(self, page, get_started_block, how_to_file_blocks, title):
        body = list(page.body.raw_data)
        changed = False

        for index, block in enumerate(body):
            if (
                block.get("id") == GET_STARTED_BLOCK_ID
                and block.get("type") == "paragraph"
            ):
                body[index] = get_started_block
                changed = True
                break

        managed_indexes = [
            index
            for index, block in enumerate(body)
            if block.get("id") in HOW_TO_FILE_BLOCK_IDS
        ]
        if managed_indexes:
            insert_at = managed_indexes[0]
            updated_body = [
                block for block in body if block.get("id") not in HOW_TO_FILE_BLOCK_IDS
            ]
            updated_body[insert_at:insert_at] = how_to_file_blocks
            if updated_body != body:
                body = updated_body
                changed = True
        else:
            insert_at = next(
                (
                    index + 1
                    for index, block in enumerate(body)
                    if block.get("id") == GET_STARTED_CARDS_BLOCK_ID
                ),
                len(body),
            )
            body[insert_at:insert_at] = how_to_file_blocks
            changed = True

        if changed:
            page.body = body
            page.save_revision().publish()
            logger.info(f"Updated the '{title}' page.")
        else:
            logger.info(f"- {title} page already includes the How to File section.")

    def create_page_info(self, home_page):
        slug = "petitioners-guidance"
        title = "Guidance for Self-Represented Petitioners (Pro Se)"

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

        computer_icon_doc = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="computer_icon.svg",
            title="computer_icon.svg",
        )
        mail_icon_doc = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="mail.svg",
            title="mail.svg",
        )
        petition_form_doc = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="Petition_Simplified_Form_2.pdf",
            title="Petition_Simplified_Form_2.pdf",
        )
        petition_kit_doc = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="Petition_Kit.pdf",
            title="Petition_Kit.pdf",
        )

        get_started_block = self.build_get_started_block(_petitioner_timeline_url)
        how_to_file_blocks = self.build_how_to_file_blocks(
            computer_icon_doc,
            mail_icon_doc,
            petition_form_doc,
            petition_kit_doc,
        )

        existing_page = Page.objects.filter(slug=slug).first()
        if existing_page:
            self.update_existing_page(
                existing_page.specific,
                get_started_block,
                how_to_file_blocks,
                title,
            )
            return

        logger.info(f"Creating the '{title}' page.")

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
                    get_started_block,
                    {
                        "type": "card",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "1",
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
                                    "numbered_icon": "2",
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
                                    "numbered_icon": "3",
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
                    *how_to_file_blocks,
                ],
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")

    def run(self):
        """Update the Petitioners Guidance page."""
        command_name = "WAG-1365: Add How to File section to Petitioners Guidance page"
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
