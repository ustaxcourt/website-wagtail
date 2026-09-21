import logging

from wagtail.documents.models import Document
from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models import IconCategories, NavigationRibbon, PetitionerExperiencePage
from home.models.snippets.call_to_action import CallToActionBox
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


PETITIONER_DOCUMENT_FILENAMES = {
    "stin": "Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
    "petition_kit": "Petition_Kit.pdf",
    "corporate_disclosure": "Corporate_Disclosure_Statement_Form.pdf",
}


class PetitionersPrepareToFilePageInitializer(PageInitializer):
    def get_document_url(self, title):
        document = Document.objects.filter(title=title).first()
        if document:
            return document.url

        logger.warning("Document with title '%s' was not found.", title)
        return f"/files/documents/{title}"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def build_page_fields(self):
        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()
        call_to_action = CallToActionBox.objects.filter(
            header="Ready to begin your petition?"
        ).first()
        stin_url = self.get_document_url(PETITIONER_DOCUMENT_FILENAMES["stin"])
        petition_kit_url = self.get_document_url(
            PETITIONER_DOCUMENT_FILENAMES["petition_kit"]
        )
        corporate_disclosure_url = self.get_document_url(
            PETITIONER_DOCUMENT_FILENAMES["corporate_disclosure"]
        )

        return {
            "navigation_ribbon": navigation_ribbon,
            "search_description": "Prepare to File",
            "introductory_text": (
                "<p>The United States Tax Court encourages electronic filing "
                "through DAWSON, the Court's electronic filing and case "
                "management system.</p><p><strong>Note:</strong> If filing "
                "using DAWSON, once you start this process you won't be able "
                "to save your work and come back to it. Petitioners who file "
                "by paper cannot immediately switch to electronic access. "
                "Consider filing electronically from the start to get "
                "electronic access to your case immediately.</p>"
            ),
            "body": [
                {
                    "type": "printable_section",
                    "value": {
                        "icon": IconCategories.CHECK,
                        "title": "Pre-Filing Checklist",
                        "intro": "<p>Have these items ready before you begin your petition.</p>",
                        "body": [
                            {
                                "type": "list",
                                "value": {
                                    "list_type": "checkbox",
                                    "items": [
                                        {
                                            "text": "<p>A copy of the IRS Notice (if you received one).</p>"
                                        },
                                        {
                                            "text": f'<p>Statement of <a href="{stin_url}">Taxpayer Identification Number (STIN)</a> form filled out with your SSN/EIN.</p>'
                                        },
                                        {
                                            "text": f'<p><a href="{petition_kit_url}">Petition Kit</a> for completion only if filing by mail.</p>'
                                        },
                                        {
                                            "text": "<p>Valid email address to register for DAWSON if filing electronically.</p>"
                                        },
                                        {
                                            "text": "<p>$60 filing fee via Pay.gov (after filing the petition).</p>"
                                        },
                                        {
                                            "text": f'<p>Complete the <a href="{corporate_disclosure_url}">Corporate Disclosure Statement</a> form ONLY if you are filing on behalf of a company.</p>'
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "paragraph",
                                "value": '<p>PLEASE NOTE: <strong><a href="/efile-a-petition">Here are the electronic filing instructions</a></strong> to help you navigate and utilize DAWSON, the United States Tax Court’s electronic filing system.</p>',
                            },
                        ],
                    },
                },
            ],
            "call_to_action": call_to_action,
        }

    def create_page_info(self, home_page):
        slug = "petitioners-prepare-to-file"
        title = "Prepare to File"
        fields = self.build_page_fields()

        existing_page = Page.objects.filter(slug=slug).first()
        if existing_page:
            page = existing_page.specific
            for field_name, value in fields.items():
                setattr(page, field_name, value)
            page.save_revision().publish()
            logger.info(f"Updated the '{title}' page with the pre-filing checklist.")
            return

        page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                slug=slug,
                seo_title=title,
                **fields,
            )
        )
        page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")

    def run(self):
        # Distinct from the original "Initialize Petitioners Prepare to File
        # page" marker so this also runs (and adds the checklist) on
        # deployments where that page was already created before this change.
        command_name = "WAG-1387: Add Pre-Filing Checklist to Prepare to File page"
        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already exists. Skipping.")
            return 0

        script_entry = ExecuteScript.create_script(command_name)
        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = (
                "Petitioners Prepare to File page updated successfully."
            )
            script_entry.save()
        except Exception as error:
            logger.error(error)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error}"
            script_entry.save()
            raise
