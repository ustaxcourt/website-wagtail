import logging
import uuid

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from search.dawson_client import get_environment_specific_dawson_url

logger = logging.getLogger(__name__)


class DawsonHowToSearchForACase(PageInitializer):
    SLUG = "dawson-how-to-search-for-a-case"
    TITLE = "How to search for a case"
    SCRIPT_NAME = "WAG-1444: Populate How to search for a case guide"
    BREADCRUMB_TITLE = "DAWSON User Guides & Electronic Filing Instructions"

    LOGO_FILENAME = "DAWSON_logo.svg"
    SCREENSHOT_FILENAME = "dawson_search_for_a_case_homepage.png"
    SCREENSHOT_TITLE = "image of the DAWSON homepage Case search tab"
    SCREENSHOT_ALT = (
        "The DAWSON homepage with the Case tab selected, showing the Search by "
        "Name form and the Search by Docket Number form"
    )

    INTRODUCTION = (
        "<p>You can search for a case in DAWSON (Docket Access Within and Secure "
        "Online Network) from the DAWSON homepage. Cases can be searched by docket "
        "number and petitioner name.</p>"
    )

    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def _screenshot_embed(self):
        image = self.load_image_from_images_dir(
            "dawson", self.SCREENSHOT_FILENAME, self.SCREENSHOT_TITLE
        )
        if image is None:
            return ""
        return (
            f'<embed alt="{self.SCREENSHOT_ALT}" embedtype="image" '
            f'format="fullwidth" id="{image.id}"/>'
        )

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
        screenshot = self._screenshot_embed()

        phases = [
            self._phase(
                "Search by Docket Number",
                "<p>You can search for a case using its docket number.</p>"
                "<p>The docket number must include the dash (for example, 123-18).</p>"
                "<p>You may, but do not have to, include the letter suffix "
                "(S, L, SL, R, X, D, or P) when searching.</p>"
                "<p>When you enter a docket number that matches a case in DAWSON, "
                "that case will display. If there is no matching case, you will "
                'receive a "No Matches Found" message.</p>'
                "<p>To search by docket number, use the <b>Case</b> tab on the "
                "DAWSON homepage.</p>"
                f"{screenshot}",
            ),
            self._phase(
                "Search by Petitioner Name",
                "<p>You can search for a case using the petitioner's full name or "
                "last name.</p>"
                "<p>Partial name searches are not currently supported. For example, "
                'entering "Ron" will not return results for "Ronald."</p>'
                "<p>You can improve your search results by filtering:</p>"
                "<ul>"
                "<li>Country</li>"
                "<li>State</li>"
                "<li>Date Filed Start Date</li>"
                "<li>Date Filed End Date</li>"
                "<li>Case Procedure</li>"
                "<li>Case Type (Docket Suffix)</li>"
                "</ul>"
                "<p>If the United States is selected, U.S. Territories and military "
                "bases are included.</p>"
                "<p>These filters are optional and may be used in any combination "
                "to refine search results.</p>"
                "<p>To search by name, use the <b>Case</b> tab on the DAWSON "
                "homepage.</p>"
                f"{screenshot}",
            ),
            self._phase(
                "Tips and Tricks",
                "<p>If your search does not return a result:</p>"
                "<ul>"
                "<li>Confirm that the docket number includes the dash.</li>"
                "<li>Confirm that the petitioner's name is entered correctly.</li>"
                "<li>Try searching using the petitioner's full last name.</li>"
                "<li>Apply filters to refine your search results.</li>"
                "</ul>",
                bubble_content="info",
            ),
        ]

        return {
            "title": self.TITLE,
            "show_title": False,
            "introduction": self.INTRODUCTION,
            "print_button_text": "Print",
            "show_numbers_in_bubbles": True,
            "phases": phases,
        }

    def build_resource_cards(self):
        logo = self.load_document_from_documents_dir(
            subdirectory=None,
            filename=self.LOGO_FILENAME,
            title=self.LOGO_FILENAME,
        )
        # Production: https://dawson.ustaxcourt.gov/; every other environment
        # points at the non-production DAWSON.
        dawson_url = f"{get_environment_specific_dawson_url()}/"
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
                                "title": "DAWSON",
                                "description": "",
                                "icon": {"svg_file": logo.pk},
                                "content_alignment": "left",
                                "link": [
                                    {
                                        "type": "external_url",
                                        "value": dawson_url,
                                        "id": str(uuid.uuid4()),
                                    }
                                ],
                            },
                            "id": str(uuid.uuid4()),
                        }
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
        """Create or populate the DAWSON How to search for a case guide."""
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
                "DAWSON How to search for a case page created or updated successfully."
            )
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
