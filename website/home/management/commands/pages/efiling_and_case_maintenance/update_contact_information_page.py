from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer

update_contact_information_images = [
    {
        "title": "Login Screen Private Practitioner Test",
        "filename": "login-screen-private-practitioner-test.jpg",
    },
    {
        "title": "Login Screen Test Petitioner",
        "filename": "login-screen-test-petitioner.jpg",
    },
    {
        "title": "Edit Petitioner Contact Info",
        "filename": "edit-petitioner-contact-info.jpg",
    },
]

update_contact_information_docs = {
    "Rule-200(2nd-amended).pdf": "",
}


class UpdateContactInformationPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "update-contact-information"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Update Contact Information"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in update_contact_information_images:
            image_uploaded = self.load_image_from_images_dir(
                "dawson", image["filename"], image["title"]
            )

            if image_uploaded:
                uploaded_images[image["filename"]] = {
                    "id": image_uploaded.id,
                    "url": image_uploaded.file.url,
                }

        for doc_name in update_contact_information_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            update_contact_information_docs[doc_name] = document

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "h2",
                        "value": "Practitioners",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": "As a practitioner, you can update your contact information by clicking on the <strong>Person Icon</strong> and then selecting <strong>My Account</strong> in the upper right corner.",
                                    "image": uploaded_images[
                                        "login-screen-private-practitioner-test.jpg"
                                    ]["id"],
                                },
                                {
                                    "text": "Updating your contact information will automatically generate a Notice of Change of Address, Notice of Change of Phone Number, or Notice of Change of Address and Phone Number that will be filed and served in each of your open cases, and any case closed within the past 6 months.",
                                },
                                {
                                    "text": """If you have changed employers (IRS to private practice/private practice to IRS), contact <a href="mailto:Admissions@ustaxcourt.gov" >admissions@ustaxcourt.gov</a> to have your employer updated in DAWSON.""",
                                },
                                {
                                    "text": (
                                        "REMINDER: Each person admitted to practice before the Court shall promptly notify the Court of any change in contact information. "
                                        f"<a href=\"{update_contact_information_docs['Rule-200(2nd-amended).pdf'].file.url}\" "
                                        "target=\"_blank\" title=\"Rule 200\">Rule 200(e)</a>, Tax Court Rules of Practice and Procedure."
                                    ),
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h2",
                        "value": "Petitioners",
                    },
                    {
                        "type": "h3",
                        "value": "Updating Petitioner Account Login and Service Email Address",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": "Petitioners who wish to update the login and service email address for a DAWSON account should click on the <strong>Person Icon</strong> and then <strong>My Account</strong> in the upper right corner of the DAWSON screen.",
                                    "image": uploaded_images[
                                        "login-screen-test-petitioner.jpg"
                                    ]["id"],
                                },
                                {
                                    "text": "Input your new email address and click <strong>Save</strong>.",
                                },
                                {
                                    "text": " A verification email from <strong>noreply@dawson.ustaxcourt.gov</strong> will be sent to your new email address. If you don’t see it, check your junk/spam folder. You must verify your new email address to change it in DAWSON. After 24 hours, the verification link will expire.",
                                },
                                {
                                    "text": "<strong>Note</strong>: Changing the DAWSON account email address impacts the whole account, not just the email address for a particular case.",
                                },
                            ],
                        },
                    },
                    {
                        "type": "h3",
                        "value": "Updating Petitioner Mailing Address and Phone Number",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": "A petitioner’s mailing address and phone number can be updated by clicking the <strong>Edit</strong> link by the petitioner’s name under the Case Information tab within a case.",
                                    "image": uploaded_images[
                                        "edit-petitioner-contact-info.jpg"
                                    ]["id"],
                                },
                                {
                                    "text": "Updating a petitioner’s mailing address or phone number will automatically generate a Notice of Change of Address, Notice of Change of Phone Number, or Notice of Change of Address and Phone Number in that specific case.",
                                },
                                {
                                    "text": "If a petitioner has more than one case, the petitioner’s mailing address and phone number will need to be updated separately in each of their cases.",
                                },
                            ],
                        },
                    },
                ],
                search_description="Learn how to update contact information",
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
