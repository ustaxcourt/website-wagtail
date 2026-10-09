import logging

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon, PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)

GETTING_STARTED_FORMS = [
    {
        "key": "stin",
        "number": "Form 4",
        "title": "Statement of Taxpayer Identification Number (STIN)",
        "description": (
            "<p>This form is required, regardless of how you file your Petition. "
            "For security purposes, upload it only when prompted as a separate "
            "document; the Court will not retain a copy. The STIN is the only "
            "document you should file with your social security number or EIN.</p>"
            "<p>The Form 4 is included in the Petition Kit for those filing in mail.</p>"
        ),
        "button": "Download Form 4",
        "card_id": "05a93f0c-0cb7-42bd-a43c-61363d7784d8",
        "button_id": "5bf7862f-2238-40ef-a9f5-df33c9302be5",
        "link_id": "41e358d1-5873-4637-81f4-da8a33e41d93",
    },
    {
        "key": "petition_kit",
        "number": "Form Collection",
        "title": "Petition Kit",
        "description": (
            "<p>The Petition Kit includes all the forms you need to start a case by mail.</p>"
        ),
        "button": "Download Petition Kit",
        "card_id": "8a4eb7e5-7b4a-43eb-a01c-c6157642cfbc",
        "button_id": "bc0f8151-e60e-4195-8c7d-fc0b9922ac2e",
        "link_id": "19e3a2ce-3e09-40fb-a4b4-a922fd88e877",
    },
    {
        "key": "petition",
        "number": "Form 2",
        "title": "Petition",
        "description": (
            "<p>You will need this form only if you plan to upload it as a PDF. "
            "You do not need it if you file using the petition generator. Form 2 "
            "is included in the petition kit for those filing by mail.</p>"
        ),
        "button": "Download Form 2",
        "card_id": "a19a1956-01c9-4ca7-8fae-616224566696",
        "button_id": "a0c61387-e4bd-4999-90ca-b4cb07274070",
        "link_id": "e06a88ba-1704-481e-a2da-419ea9d88f56",
    },
]

SPECIAL_CIRCUMSTANCES_FORMS = [
    {
        "key": "fee_waiver",
        "number": "Form",
        "title": "Application for Waiver of Filing Fee",
        "description": (
            "<p>File this form if you cannot afford the $60 filing fee only after "
            "your petition has been served, and would like to request a waiver "
            "based on demonstrated financial need.</p>"
        ),
        "button": "Download Waiver Application",
        "card_id": "52a76785-108e-4a83-8977-6a5d2cb5d42c",
        "button_id": "e65d1867-56ab-4ae9-b9d6-635ec641470a",
        "link_id": "c3262764-4997-4304-8b2e-7ecf08aa0503",
    },
    {
        "key": "corporate_disclosure",
        "number": "Form 6",
        "title": "Corporate Disclosure Statement",
        "description": (
            "<p>This form must accompany a petition filed by an entity to identify "
            "any parent corporation or publicly held corporation owning 10% or more "
            "of the entity\u2019s stock. If the entity has none, fill out the form "
            "accordingly.</p>"
        ),
        "button": "Download Form 6",
        "card_id": "a0b1dc9b-ce1d-498a-8af4-24c4ed75a4e3",
        "button_id": "a8d444e6-6a02-47ca-b482-0f87c9540a98",
        "link_id": "f198d580-1211-4507-910c-a0c385d9dadc",
    },
    {
        "key": "remote_motion",
        "number": "Form",
        "title": "Motion to Proceed Remotely",
        "description": (
            "<p>File this form to request a remote trial only after your petition "
            "has been served. Even if you request a remote proceeding you must still "
            '<a href="/dpt-cities">pick a place of trial</a>.</p>'
        ),
        "button": "Download Motion Template",
        "card_id": "b6b7fdb5-1d49-4caa-9944-b8095f24a91e",
        "button_id": "eeb99465-3194-47aa-9c8d-e593ec1f7843",
        "link_id": "97d476b2-c767-42b5-af20-139430044343",
    },
]

FORM_DOCUMENT_FILENAMES = {
    "stin": "Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
    "petition_kit": "Petition_Kit.pdf",
    "petition": "Petition_Simplified_Form_2.pdf",
    "fee_waiver": "Application_for_Waiver_of_Filing_Fee.pdf",
    "corporate_disclosure": "Corporate_Disclosure_Statement_Form.pdf",
    "remote_motion": "Motion_to_Proceed_Remotely.pdf",
}

MANAGED_BODY_BLOCK_IDS = {
    "31117854-55ac-458b-944a-70961a3bf5b6",
    "4d04948e-e56b-4cd7-ab54-30dfc22098ec",
    "d793fe7d-1e1a-4b4d-b8d9-a615e68ae129",
    "c4490303-b368-49f7-9b1f-858d035dfae1",
    "9ed4dbd5-b712-4f1e-8dc4-1b3bfa246d60",
    "81a1441d-89c3-456b-95b5-9666d32d541b",
    "db314192-839f-4fc1-8679-1d2fb2ef7c7f",
}


class PetitionersFormsPageInitializer(PageInitializer):
    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def _load_documents(self):
        documents = {
            key: self.load_document_from_documents_dir(
                subdirectory=None,
                filename=filename,
                title=filename,
            )
            for key, filename in FORM_DOCUMENT_FILENAMES.items()
        }
        article_icon = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="icon-article.svg",
            title="Icon: Article (Forms to File a Petition)",
        )
        download_icon = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="download_icon.svg",
            title="Download",
        )
        return documents, article_icon, download_icon

    @staticmethod
    def _build_form_card(form, documents, article_icon, download_icon):
        return {
            "type": "item",
            "value": {
                "color": "gray",
                "numbered_icon": "",
                "numbered_icon_alignment": "left",
                "title_icon": article_icon.pk,
                "title_icon_alt_text": "",
                "subtitle": form["number"],
                "title": form["title"],
                "description": form["description"],
                "buttons": [
                    {
                        "type": "item",
                        "value": {
                            "icon": download_icon.pk,
                            "icon_location": "before",
                            "text": form["button"],
                            "url": [
                                {
                                    "type": "internal_pdf",
                                    "value": documents[form["key"]].pk,
                                    "id": form["link_id"],
                                }
                            ],
                            "style": "primary",
                            "button_hover": True,
                            "helper_text": "",
                            "download": True,
                        },
                        "id": form["button_id"],
                    }
                ],
            },
            "id": form["card_id"],
        }

    def build_page_body(self, documents, article_icon, download_icon):
        return [
            {
                "type": "h2",
                "value": "Getting Started",
                "id": "31117854-55ac-458b-944a-70961a3bf5b6",
            },
            {
                "type": "paragraph",
                "value": (
                    "Download one of the following based on your chosen to file method."
                ),
                "id": "4d04948e-e56b-4cd7-ab54-30dfc22098ec",
            },
            {
                "type": "card",
                "value": [
                    self._build_form_card(form, documents, article_icon, download_icon)
                    for form in GETTING_STARTED_FORMS
                ],
                "id": "d793fe7d-1e1a-4b4d-b8d9-a615e68ae129",
            },
            {
                "type": "h2",
                "value": "Special Circumstances",
                "id": "c4490303-b368-49f7-9b1f-858d035dfae1",
            },
            {
                "type": "paragraph",
                "value": (
                    "Download one of the following based on your situation. Most "
                    "motions do not require a specific form ("
                    '<a href="/files/documents/rule-50.pdf">'
                    "TITLE V. MOTIONS RULE 50. GENERAL REQUIREMENTS</a>)."
                ),
                "id": "9ed4dbd5-b712-4f1e-8dc4-1b3bfa246d60",
            },
            {
                "type": "card",
                "value": [
                    self._build_form_card(form, documents, article_icon, download_icon)
                    for form in SPECIAL_CIRCUMSTANCES_FORMS
                ],
                "id": "81a1441d-89c3-456b-95b5-9666d32d541b",
            },
            {
                "type": "callout",
                "value": {
                    "heading": "Note:",
                    "text": (
                        "<p>Most forms are fillable PDFs. You can type your information "
                        "directly into the form before printing, or you can print the "
                        "forms and write clearly in black or blue ink.</p>"
                    ),
                    "callout_type": "info",
                },
                "id": "db314192-839f-4fc1-8679-1d2fb2ef7c7f",
            },
        ]

    def update_existing_page(self, page, body):
        current_body = list(page.body.raw_data)
        managed_indexes = [
            index
            for index, block in enumerate(current_body)
            if block.get("id") in MANAGED_BODY_BLOCK_IDS
        ]
        if managed_indexes:
            insert_at = managed_indexes[0]
            updated_body = [
                block
                for block in current_body
                if block.get("id") not in MANAGED_BODY_BLOCK_IDS
            ]
            updated_body[insert_at:insert_at] = body
        else:
            updated_body = current_body + body

        if updated_body != current_body:
            page.body = updated_body
            page.save_revision().publish()
            logger.info("Updated the Forms to File a Petition page.")

    def create_page_info(self, home_page):
        slug = "petitioners-forms"
        title = "Forms to File a Petition"
        documents, article_icon, download_icon = self._load_documents()
        body = self.build_page_body(documents, article_icon, download_icon)

        existing_page = Page.objects.filter(slug=slug).first()
        if existing_page:
            self.update_existing_page(existing_page.specific, body)
            return

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()
        call_to_action = CallToActionBox.objects.filter(
            header="Ready to begin your petition?"
        ).first()
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                introductory_text="Download forms you may need.",
                call_to_action=call_to_action,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                body=body,
            )
        )
        new_page.save_revision().publish()
        logger.info("Created the Forms to File a Petition page.")

    def run(self):
        command_name = "Create editable forms content for Forms to File a Petition"
        if ExecuteScript.command_exists(command_name):
            logger.info("Script '%s' already exists. Skipping.", command_name)
            return 0

        script_entry = ExecuteScript.create_script(command_name)
        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = (
                "Forms to File a Petition page content updated successfully."
            )
            script_entry.save()
        except Exception as error:
            logger.exception("Failed to update the Forms to File a Petition page.")
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error}"
            script_entry.save()
            raise
