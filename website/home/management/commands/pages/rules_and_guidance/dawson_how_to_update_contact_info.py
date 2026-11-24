from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
import logging
import uuid
from home.models.utils.execute_script import ExecuteScript
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from search.dawson_client import get_environment_specific_dawson_url


logger = logging.getLogger(__name__)
PAGE_SLUG = "dawson-how-to-update-contact-info"
CREATE_COMMAND_NAME = "WAG-1450: How to update contact information"
RESOURCES_COMMAND_NAME = (
    "WAG-1447: Add resource cards to How to update contact information"
)
REMOVE_NAVIGATION_RIBBON_COMMAND_NAME = (
    "WAG-1447: Remove Navigation Ribbon on How to update contact information"
)
RESTORE_BODY_COMMAND_NAME = (
    "WAG-1447: Restore missing timeline body on How to update contact information"
)
DAWSON_ICON_FILENAME = "DAWSON_icon.svg"

images_in_timeline = {
    "edit_petitioner_contact_info": {
        "title": "Edit Petitioner Contact Info",
        "filename": "edit-petitioner-contact-info.jpg",
    },
    "login_screen_test_petitioner": {
        "title": "Login Screen Test Petitioner",
        "filename": "login-screen-test-petitioner.jpg",
    },
    "login_screen_private_practitioner_test": {
        "title": "Login Screen Private Practitioner Test",
        "filename": "login-screen-private-practitioner-test.jpg",
    },
}

update_contact_info_resources = [
    (
        "DAWSON",
        get_environment_specific_dawson_url(),
    ),
]


class DawsonHowToUpdateContactInfo(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def build_resource_cards(self):
        icon = self.load_document_from_documents_dir(
            subdirectory=None,
            filename=DAWSON_ICON_FILENAME,
            title=DAWSON_ICON_FILENAME,
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
                        for title, url in update_contact_info_resources
                    ],
                },
                "id": str(uuid.uuid4()),
            }
        ]

    def remove_navigation_ribbon(self):
        """The page should not have a navigation ribbon, so remove it if it exists."""
        page = PetitionerExperiencePage.objects.filter(slug=PAGE_SLUG).first()
        if page is None:
            logger.warning(
                f"Page '{PAGE_SLUG}' not found; navigation ribbon unchanged."
            )
            return

        body = page.body.get_prep_value()
        changed = False

        if page.navigation_ribbon:
            page.navigation_ribbon = None
            changed = True

        if not changed:
            return

        page.body = body
        page.save_revision().publish()

    def restore_missing_body(self):
        """Restore the initializer's timeline only when the existing page body is empty."""
        page = Page.objects.filter(slug=PAGE_SLUG).first()
        if page is None:
            self._check_parent()
            self.create()
            return

        page = page.specific
        if not isinstance(page, PetitionerExperiencePage):
            raise TypeError(
                f"Page '{PAGE_SLUG}' must be a PetitionerExperiencePage, "
                f"not {type(page).__name__}."
            )
        if page.body:
            logger.info(
                f"Page '{PAGE_SLUG}' already has body content; leaving it unchanged."
            )
            return

        logger.info(f"Restoring the missing body on page '{PAGE_SLUG}'.")
        self.create_page_info(Page.objects.get(slug="home"), update_existing=True)

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

    def create_page_info(self, home_page, update_existing=False):
        slug = "dawson-how-to-update-contact-info"
        title = "How to update contact information"

        existing_page = Page.objects.filter(slug=slug).first()
        if existing_page:
            existing_page = existing_page.specific
            if not update_existing or existing_page.body:
                logger.info(f"- {title} page already exists.")
                return
            if not isinstance(existing_page, PetitionerExperiencePage):
                raise TypeError(
                    f"Page '{slug}' must be a PetitionerExperiencePage, "
                    f"not {type(existing_page).__name__}."
                )

        for key in images_in_timeline.keys():
            key["id"] = None
            image = self.load_image_from_images_dir(
                subdirectory=None,
                filename=key["filename"],
                title=key["title"],
            )
            if image:
                key["id"] = image.pk

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
                            "title": "How to update contact information",
                            "introduction": '<p data-block-key="6pwx6">Learn how to update your email address, mailing address, phone number, and other contact information in DAWSON. The steps you need to follow may differ depending on whether you are a practitioner or a petitioner.</p>',
                            "print_button_text": "Print",
                            "show_title": False,
                            "warning_callout": {"heading": "", "text": ""},
                            "show_numbers_in_bubbles": True,
                            "phases": [
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Practitioner",
                                        "default_to_open": False,
                                        "date_range": "",
                                        "bubble_content": "scale",
                                        "instructions": f'<p data-block-key="2y5fl"><b>Updating Practitioner Contact Information and Service Email Address</b></p><p data-block-key="b1ip7">As a practitioner, you can update your contact information by clicking on the Person Icon and then selecting My Account in the upper right corner.</p><ul><li data-block-key="3qgp5">Updating your contact information will automatically generate a Notice of Change of Address, Notice of Change of Phone Number, or Notice of Change of Address and Phone Number that will be filed and served in each of your open cases, and any case closed within the past 6 months.</li><li data-block-key="3psq9">Updating your email address will not automatically generate a Notice of Change of Email Address.<ul><li data-block-key="4lu9a">A verification email from <a href="mailto:noreply@dawson.ustaxcourt.gov">noreply@dawson.ustaxcourt.gov</a> will be sent to your new email address. If you don’t see it, check your junk/spam folder. You must verify your new email address to change it in DAWSON. After 24 hours, the verification link will expire.</li></ul></li></ul><p data-block-key="7t58h"></p><embed embedtype="image" format="fullwidth" id="{images_in_timeline["login_screen_private_practitioner_test"]["id"]}" alt=""/><p data-block-key="5c0vg"><br/><b>Updating Practitioner Employer Information</b></p><ul><li data-block-key="7d9hj">If you have changed employers (IRS to private practice/private practice to IRS), contact <a href="mailto:admissions@ustaxcourt.gov">admissions@ustaxcourt.gov</a> to have your employer updated in DAWSON.</li><li data-block-key="cfsek">REMINDER: Each person admitted to practice before the Court shall promptly notify the Court of any change in contact information. Rule 200(e), Tax Court Rules of Practice and Procedure.</li></ul>',
                                        "your_tasks": [],
                                        "helpful_information": [],
                                    },
                                    "id": "2224e788-57e4-4866-a76e-0b5552f200c9",
                                },
                                {
                                    "type": "phase",
                                    "value": {
                                        "title": "Petitioner",
                                        "default_to_open": False,
                                        "date_range": "",
                                        "bubble_content": "user",
                                        "instructions": f'<p data-block-key="2y5fl"><b>Updating Petitioner Account Login and Service Email Address</b></p><p data-block-key="48d99">Petitioners who wish to update the login and service email address for a DAWSON account should click on the Person Icon and then My Account in the upper right corner of the DAWSON screen.</p><p data-block-key="dtm36"></p><p data-block-key="dt4fc"></p><embed embedtype="image" format="fullwidth" id="{images_in_timeline["login_screen_test_petitioner"]["id"]}" alt=""/><p data-block-key="1jniv"><br/></p><ul><li data-block-key="5r5ju">Input your new email address and click Save.<ul><li data-block-key="3n4ce">A verification email from <a href="mailto:noreply@dawson.ustaxcourt.gov">noreply@dawson.ustaxcourt.gov</a> will be sent to your new email address. If you don’t see it, check your junk/spam folder. You must verify your new email address to change it in DAWSON. After 24 hours, the verification link will expire.</li></ul></li><li data-block-key="bjs4a">Note: Changing the DAWSON account email address impacts the whole account, not just the email address for a particular case. Updating the service email address will automatically generate a Notice of Change of Email Address in each of your open cases, and any case closed within the past 6 months.</li></ul><p data-block-key="eevip"><b>Updating Petitioner Mailing Address and Phone Number</b></p><p data-block-key="cm0o4">A petitioner’s mailing address and phone number can be updated by clicking the Edit link by the petitioner’s name under the <b>Case Information</b> tab within a case.</p><p data-block-key="6v2tt"></p><embed embedtype="image" format="fullwidth" id="{images_in_timeline["edit_petitioner_contact_info"]["id"]}" alt=""/><p data-block-key="72eun"><br/></p><ul><li data-block-key="1chpe">Updating a petitioner’s mailing address or phone number will automatically generate a Notice of Change of Address, Notice of Change of Phone Number, or Notice of Change of Address and Phone Number in that specific case.</li><li data-block-key="ervmp">If a petitioner has more than one case, the petitioner’s mailing address and phone number will need to be updated separately in each of their cases.</li></ul>',
                                        "your_tasks": [],
                                        "helpful_information": [],
                                    },
                                    "id": "855f46e5-a0b1-44f3-b3ed-33fb44a2b7ec",
                                },
                            ],
                        },
                        "id": "d284d4e1-ac72-40b3-be85-48a4526b9821",
                    }
                ],
            )
        )

        new_page.save_revision().publish()

    # def run(self):
    #     """Update the Dawson How to update contact information"""
    #     command_name = "WAG-1450: How to update contact information"
    #     # Check if script already exists
    #     if ExecuteScript.command_exists(command_name):
    #         logger.info(f"Script '{command_name}' already exists. Skipping.")
    #         return 0

    #     # Check before recording the script so a missing parent page is retried
    #     # on the next deploy instead of being permanently marked as run.
    #     if not Page.objects.filter(slug="dawson-user-guides").exists():
    #         raise Exception(
    #             f"'dawson-user-guides' page not found; cannot run '{command_name}'."
    #         )

    #     script_entry = ExecuteScript.create_script(command_name)

    #     try:
    #         self.create()
    #         execution_log_text = (
    #             "Dawson How to update contact information page updated successfully."
    #         )
    #         script_entry.execution_status = "SUCCESS"
    #         script_entry.execution_log = execution_log_text
    #         script_entry.save()

    #     except Exception as e:
    #         logger.error(e)
    #         script_entry.execution_status = "FAILURE"
    #         script_entry.execution_log = f"<strong>Error:</strong> {e}"
    #         script_entry.save()
    #         raise

    def run(self):
        """Create the Dawson How to troubleshoot file upload errors page and its resource cards"""
        page = Page.objects.filter(slug=PAGE_SLUG).first()
        if page and page.has_unpublished_changes:
            logger.warning(
                f"Page '{PAGE_SLUG}' has unpublished changes; deferring initializer updates."
            )
            return 0

        created = self._run_once(CREATE_COMMAND_NAME, self.create, self._check_parent)
        updated = self._run_once(RESOURCES_COMMAND_NAME, self.add_resource_cards)
        restored = self._run_once(RESTORE_BODY_COMMAND_NAME, self.restore_missing_body)
        retitled = self._run_once(
            REMOVE_NAVIGATION_RIBBON_COMMAND_NAME, self.remove_navigation_ribbon
        )
        if not (created or updated or restored or retitled):
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
