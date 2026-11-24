import logging
import uuid

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)

PAY_GOV_HOME_URL = "https://www.pay.gov/public/home"
PAY_GOV_PETITION_FEES_FORM_URL = "https://www.pay.gov/public/form/start/60485840"
# The superseded Rule 11 is not one of the site's documents, so this stays external.
RULE_11_URL = "https://ustaxcourt.gov/resources/ropp/Rule-11(superseded).pdf"

CLERK_ADDRESS = (
    "<p><b>Clerk of the Court<br/>United States Tax Court<br/>"
    "400 Second Street, NW<br/>Washington, DC 20217</b></p>"
)


class DawsonHowToPayFilingFee(PageInitializer):
    SLUG = "dawson-how-to-pay-filing-fee"
    TITLE = "How to pay the filing fee"
    SCRIPT_NAME = "WAG-1442: Populate How to pay the filing fee guide"
    BREADCRUMB_TITLE = "DAWSON User Guides & Electronic Filing Instructions"

    OPEN_IN_NEW_ICON_FILENAME = "open_in_new.svg"
    WAIVER_FILENAME = "Application_for_Waiver_of_Filing_Fee.pdf"
    DOCUMENT_FILENAMES = {"waiver": WAIVER_FILENAME}

    # (key, filename in management/images/dawson, image title, alt text)
    IMAGES = {
        "form_start": (
            "dawson_pay_fee_form_start.png",
            "image of the Pay.gov Tax Court Petitions Fees start page",
            "The pay.gov US Tax Court Fees - Petitions start page with the "
            "Continue to the Form button",
        ),
        "agency_form": (
            "dawson_pay_fee_agency_form.png",
            "image of the Pay.gov Tax Court Petitions Fees agency form",
            "The pay.gov US Tax Court Fees - Petitions form with fields for name, "
            "address, docket number and payment amount",
        ),
        "payment_info": (
            "dawson_pay_fee_payment_info.png",
            "image of the Pay.gov Tax Court Petitions Fees payment information page",
            "The pay.gov Enter Payment Info step, where you choose how to pay",
        ),
    }

    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def _embed(self, key):
        filename, title, alt = self.IMAGES[key]
        image = self.load_image_from_images_dir("dawson", filename, title)
        if image is None:
            return ""
        return (
            f'<embed alt="{alt}" embedtype="image" format="fullwidth" id="{image.id}"/>'
        )

    def _waiver_url(self):
        """The uploaded waiver form, so the link stays in this environment."""
        return self.load_document_from_documents_dir(
            subdirectory=None,
            filename=self.WAIVER_FILENAME,
            title=self.WAIVER_FILENAME,
        ).url

    @staticmethod
    def _phase(title, instructions, bubble_content="number"):
        return {
            "type": "phase",
            "value": {
                "title": title,
                "default_to_open": True,
                "date_range": "",
                "bubble_content": bubble_content,
                "instructions": instructions,
                "your_tasks": [],
                "helpful_information": [],
            },
            "id": str(uuid.uuid4()),
        }

    def build_timeline(self):
        waiver_url = self._waiver_url()
        waiver_link = f'<a href="{waiver_url}">Application for Waiver of Filing Fee</a>'

        introduction = (
            f'<p>The Court uses <a href="{PAY_GOV_HOME_URL}">pay.gov</a> for '
            "processing payments. Filing fees are required to submit a petition. "
            "The Court’s filing fee is $60 and may be paid online, by mail, or "
            f"in person. The fee may be waived by filing an {waiver_link}. Your "
            "petition must be processed by the Court before the Application for "
            "Waiver of Filing fee can be filed electronically.</p>"
        )

        online = (
            "<ul><li>To pay the filing fee online, complete the "
            f'<a href="{PAY_GOV_PETITION_FEES_FORM_URL}">Tax Court Petitions Fees '
            "form</a>.</li></ul>"
            f"{self._embed('form_start')}"
            "<ul><li>Click <b>Continue to the Form</b>.</li></ul>"
            f"{self._embed('agency_form')}"
            "<ul>"
            "<li>Fill out personal details, including your U.S. Tax Court Docket "
            "Number(s). Docket Number(s) should be entered in xxxxx-xx format "
            "(e.g., 12345-20)."
            "<ul>"
            "<li>If your docket number includes a suffix at the end, do not enter "
            "the suffix on the form. <b>For example</b>, if the docket number is "
            '12345-20L, enter 12345-20 and omit the "L".</li>'
            "<li>If you filed electronically with DAWSON, the Court’s "
            "electronic case management system, you received your Docket Number on "
            "the confirmation screen. It is also listed by your case on your "
            "dashboard.</li>"
            "<li>If you submitted your petition by mail, you received your Docket "
            "Number in the mail on the Notice of Receipt of Petition document.</li>"
            "</ul></li>"
            "<li>Click <b>Continue</b>.</li>"
            "</ul>"
            f"{self._embed('payment_info')}"
            "<ul>"
            "<li>Confirm how you would like to pay.</li>"
            "<li>Click <b>Next</b>.</li>"
            "<li>Enter payment information.</li>"
            "<li>Click <b>Review</b> and <b>Submit Payment</b>.</li>"
            "<li>Print Confirmation Page</li>"
            "</ul>"
            "<p><b>Tips and Tricks</b></p>"
            "<ul>"
            "<li>Be sure to have the Docket Number(s) handy for reference during "
            "the payment process.</li>"
            "<li>You can also access the pay.gov site directly from DAWSON, if you "
            "have a DAWSON account.</li>"
            "</ul>"
        )

        # The mockup shows this notice in a light blue callout box. A phase only
        # holds rich text, so it is a bold heading and paragraphs here.
        by_mail = (
            "<p>To pay the filing fee by mail, make checks/money orders payable "
            "to:</p>"
            f"{CLERK_ADDRESS}"
            "<p>Include petitioner(s)' name(s) and Docket Number(s) on the "
            "check.</p>"
            "<p><b>NOTICE TO CUSTOMERS MAKING PAYMENT BY CHECK</b></p>"
            "<p>If a fee is paid by check, money order, or other draft, it should "
            "be payable to “Clerk, United States Tax Court”. "
            f'(<a href="{RULE_11_URL}">Rule 11</a>, Tax Court Rules of Practice '
            "and Procedure). Cash, checks or money orders may be mailed to: United "
            "States Tax Court, 400 Second Street, N.W., Washington, D.C. 20217.</p>"
            "<p>Any check sent to the U.S. Tax Court will be converted into an "
            "electronic funds transfer (EFT). We will scan your check and use the "
            "account information on it to electronically debit your account for the "
            "amount of the check. The debit from your account will usually occur "
            "within 24 hours and will be shown on your regular account "
            "statement.</p>"
            "<p>We will not return your original check. It will be destroyed, but "
            "we will keep an electronic copy. If the EFT could not be processed "
            "for technical reasons, your submission of the check for payment "
            "authorizes us to process the electronic copy in place of the original "
            "check. If the EFT could not be completed because of insufficient "
            "funds, we may try to make the transfer up to two times.</p>"
            "<p>Privacy Information - The United States Tax Court’s authority "
            "to collect fees associated with case processing is documented under "
            "Title 26 United States Code Sections 7451 &amp; 7471 through 7475. "
            "Information captured from checks received will be strictly used in "
            "accordance with the petitioner’s request to process their "
            "respective cases. Furnishing the check information is voluntary, but "
            "a decision not to do so may require you to make payment by some other "
            "method.</p>"
        )

        other_options = (
            "<p>Can't afford to pay the filing fee? Submit an "
            f"{waiver_link}. This form is a fillable PDF.</p>"
            "<ol>"
            "<li>Fill in the form.</li>"
            "<li>Print the form, or save the file to your computer.</li>"
            "<li>File the form to your case:"
            "<ul>"
            "<li>If you filed your petition electronically in DAWSON, you may "
            "upload the application to your case.</li>"
            "<li>If you filed your petition by paper, hand deliver or mail the "
            "application to the address below:</li>"
            "</ul></li>"
            "</ol>"
            f"{CLERK_ADDRESS}"
        )

        return {
            "title": self.TITLE,
            "show_title": False,
            "introduction": introduction,
            "print_button_text": "Print",
            "show_numbers_in_bubbles": True,
            "phases": [
                self._phase("How to Pay the Filing Fee Online", online),
                self._phase(
                    "How to Pay the Filing Fee by Mail, or in Person",
                    by_mail,
                    bubble_content="info",
                ),
                self._phase("Other Filing Fee Options", other_options),
            ],
        }

    def build_resource_cards(self):
        icon = self.load_document_from_documents_dir(
            subdirectory=None,
            filename=self.OPEN_IN_NEW_ICON_FILENAME,
            title=self.OPEN_IN_NEW_ICON_FILENAME,
        )
        tiles = [
            (
                "United States Tax Court Fees - Petitions",
                PAY_GOV_PETITION_FEES_FORM_URL,
            ),
            ("Application for Waiver of Filing Fee", self._waiver_url()),
        ]
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
                        for title, url in tiles
                    ],
                },
                "id": str(uuid.uuid4()),
            }
        ]

    def create_page_info(self, home_page):
        user_guides_page = Page.objects.get(slug="dawson-user-guides")
        breadcrumb = [
            {
                "type": "breadcrumb",
                "value": {
                    "breadcrumb_title": self.BREADCRUMB_TITLE,
                    "breadcrumb_page": [
                        {"type": "internal_page", "value": user_guides_page.id}
                    ],
                },
            }
        ]

        existing_page = Page.objects.filter(slug=self.SLUG).first()
        if existing_page:
            page = existing_page.specific
            if not isinstance(page, PetitionerExperiencePage):
                raise TypeError(
                    f"Page '{self.SLUG}' must be a Petitioner Experience page."
                )
            # Only fill in the empty page the WAG-1450 script created; never
            # overwrite content an editor has already added.
            if page.body:
                logger.info(f"- {self.TITLE} page already has content.")
                return

            logger.info(f"Populating the existing '{self.TITLE}' page.")
            # The WAG-1450 placeholder was titled "How to Pay Filing Fee".
            page.title = self.TITLE
            page.seo_title = self.TITLE
            page.search_description = self.TITLE
            page.breadcrumb = breadcrumb
            # No navigation ribbon: the Figma guide has none, and the page
            # template only applies the guide styling to pages without one.
            page.navigation_ribbon = None
            page.body = [{"type": "detailed_timeline", "value": self.build_timeline()}]
            if not page.resource_cards:
                page.resource_cards = self.build_resource_cards()
            page.save_revision().publish()
            return

        logger.info(f"Creating the '{self.TITLE}' page.")
        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=self.TITLE,
                slug=self.SLUG,
                seo_title=self.TITLE,
                navigation_ribbon=None,
                search_description=self.TITLE,
                breadcrumb=breadcrumb,
                show_floating_definitions_button=True,
                body=[{"type": "detailed_timeline", "value": self.build_timeline()}],
                resource_cards=self.build_resource_cards(),
            )
        )
        new_page.save_revision().publish()

    def run(self):
        """Create or populate the DAWSON How to pay the filing fee guide."""
        if ExecuteScript.command_exists(self.SCRIPT_NAME):
            logger.info(f"Script '{self.SCRIPT_NAME}' already exists. Skipping.")
            return 0

        # Check before recording the script so a missing parent page is retried
        # on the next deploy instead of being permanently marked as run.
        if not Page.objects.filter(slug="dawson-user-guides").exists():
            raise Exception(
                f"'dawson-user-guides' page not found; cannot run '{self.SCRIPT_NAME}'."
            )

        script_entry = ExecuteScript.create_script(self.SCRIPT_NAME)

        try:
            self.create()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = (
                "DAWSON How to pay the filing fee page created or updated successfully."
            )
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
