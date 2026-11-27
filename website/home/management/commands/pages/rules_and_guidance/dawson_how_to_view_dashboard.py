import logging
import uuid

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.management.commands.pages.rules_and_guidance.side_card_seed_data import (
    add_need_legal_help_side_card,
)
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript

logger = logging.getLogger(__name__)


class DawsonHowToViewDashboard(PageInitializer):
    SLUG = "dawson-how-to-view-dashboard"
    TITLE = "How to view the DAWSON dashboard"
    SCRIPT_NAME = "WAG-1448: Populate How to view the DAWSON dashboard guide"
    BREADCRUMB_TITLE = "DAWSON User Guides & Electronic Filing Instructions"

    PDF_ICON_FILENAME = "PDF_icon.svg"
    ACCOUNT_BALANCE_ICON_FILENAME = "icon-account-balance.svg"

    DOCUMENT_FILENAMES = {
        "petitioner_guide": "DAWSON_Petitioner_Training_Guide.pdf",
        "practitioner_guide": "DAWSON_Practitioner_Training_Guide.pdf",
    }

    # (key, filename in management/images/dawson, image title, alt text)
    IMAGES = {
        "access": (
            "dawson_dashboard_access.png",
            "image of the DAWSON dashboard before filing a petition",
            "A DAWSON dashboard for a user who has not filed a petition, showing "
            "the Welcome to DAWSON message and the Create a Case button",
        ),
        "cases": (
            "dawson_dashboard_cases.png",
            "image of the DAWSON dashboard with open and closed cases",
            "A DAWSON dashboard with Open Cases and Closed Cases tabs and a list "
            "of cases with docket number, case title, filed date and filing fee",
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

    @staticmethod
    def _phase(title, instructions, bubble_content="number"):
        return {
            "type": "phase",
            "value": {
                "title": title,
                "default_to_open": False,
                "date_range": "",
                "bubble_content": bubble_content,
                "instructions": instructions,
                "your_tasks": [],
                "helpful_information": [],
            },
            "id": str(uuid.uuid4()),
        }

    def build_timeline(self):
        phases = [
            self._phase(
                "Access Your Dashboard",
                "<p>After signing in to DAWSON, your dashboard serves as the "
                "starting point for accessing your cases, filing a petition, and "
                "finding Court resources.</p>"
                "<p>To return to your dashboard from anywhere within DAWSON, select "
                "<b>My Cases</b>.</p>"
                f"{self._embed('access')}"
                "<p>Once you have filed a petition, you can view all of your cases "
                "(open and closed) on your dashboard.</p>"
                "<p>Open cases and closed cases are displayed on separate tabs. The "
                "number of cases in each are displayed in parentheses.</p>"
                "<p>It is typical for a self-represented (pro se) petitioner to "
                "have just one case.</p>"
                "<p>The default display is 100 cases. If you would like to view "
                "more cases, use the paginator that is located at either the top "
                "of the case list or the bottom of the page to see the next 100 "
                "results.</p>"
                f"{self._embed('cases')}",
            ),
            self._phase(
                "Tips and Tricks",
                "<ul>"
                "<li>To return to your dashboard from anywhere within DAWSON, click "
                "<b>My Cases</b>.</li>"
                "<li>Open cases and closed cases are displayed on separate tabs. "
                "The number of cases for each is displayed in parentheses.</li>"
                "<li>It is typical for a self-represented (pro se) petitioner to "
                "have just one case.</li>"
                "<li>The default display is 100 cases. If you would like to view "
                "more cases, use the paginator that is located at either the top "
                "of the case list or the bottom of the page to see the next 100 "
                "results.</li>"
                "</ul>",
                bubble_content="info",
            ),
        ]

        return {
            "title": self.TITLE,
            "show_title": False,
            "introduction": (
                "<p>Your dashboard is your main landing page once you are signed "
                "in to DAWSON.</p>"
                "<p>The information available on your dashboard depends on whether "
                "you have filed a petition with the Court.</p>"
            ),
            "print_button_text": "Print",
            "show_numbers_in_bubbles": True,
            "phases": phases,
        }

    def _icon(self, filename):
        return self.load_document_from_documents_dir(
            subdirectory=None, filename=filename, title=filename
        )

    def _document_link(self, filename):
        """A link to an uploaded document, so it stays in this environment."""
        document = self.load_document_from_documents_dir(
            subdirectory=None, filename=filename, title=filename
        )
        return {"type": "external_url", "value": document.url}

    @staticmethod
    def _page_link(slug, fallback_url):
        """A link to a Wagtail page, or its public URL if the page is missing."""
        page = Page.objects.filter(slug=slug).first()
        if page:
            return {"type": "related_page", "value": page.pk}
        logger.warning(f"'{slug}' page not found - linking to {fallback_url}.")
        return {"type": "external_url", "value": fallback_url}

    @staticmethod
    def _tile(title, icon, link):
        return {
            "type": "item",
            "value": {
                "title": title,
                "description": "",
                "icon": {"svg_file": icon.pk},
                "content_alignment": "left",
                "link": [{**link, "id": str(uuid.uuid4())}],
            },
            "id": str(uuid.uuid4()),
        }

    def build_resource_cards(self):
        pdf_icon = self._icon(self.PDF_ICON_FILENAME)
        account_balance_icon = self._icon(self.ACCOUNT_BALANCE_ICON_FILENAME)
        files = self.DOCUMENT_FILENAMES
        return [
            {
                "type": "quick_access_tiles",
                "value": {
                    "tiles_hover_enabled": True,
                    "icon_position": "desktop_top_mobile_left",
                    "tiles": [
                        self._tile(
                            "DAWSON Self-Represented (Pro se) Electronic Filing "
                            "Instructions",
                            pdf_icon,
                            self._document_link(files["petitioner_guide"]),
                        ),
                        self._tile(
                            "DAWSON Practitioner Electronic Filing Instructions",
                            pdf_icon,
                            self._document_link(files["practitioner_guide"]),
                        ),
                        self._tile(
                            "Case Related Forms",
                            pdf_icon,
                            self._page_link(
                                "case-related-forms",
                                "https://ustaxcourt.gov/case-related-forms/",
                            ),
                        ),
                        self._tile(
                            "Places of Trial",
                            account_balance_icon,
                            self._page_link(
                                "dpt-cities", "https://ustaxcourt.gov/dpt-cities"
                            ),
                        ),
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
            page.breadcrumb = breadcrumb
            # No navigation ribbon: the Figma guide has none, and the page
            # template only applies the guide styling to pages without one.
            page.navigation_ribbon = None
            page.body = [{"type": "detailed_timeline", "value": self.build_timeline()}]
            if not page.resource_cards:
                page.resource_cards = self.build_resource_cards()
            page.save_revision().publish()
            if not page.side_cards.exists():
                add_need_legal_help_side_card(self, page)
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
        add_need_legal_help_side_card(self, new_page)

    def run(self):
        """Create or populate the DAWSON How to view the DAWSON dashboard guide."""
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
                "DAWSON How to view the DAWSON dashboard page created or updated "
                "successfully."
            )
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
