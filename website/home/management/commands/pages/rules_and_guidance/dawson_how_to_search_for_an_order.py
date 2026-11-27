import logging
import uuid

from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from search.dawson_client import get_environment_specific_dawson_url

logger = logging.getLogger(__name__)


class DawsonHowToSearchForAnOrder(PageInitializer):
    SLUG = "dawson-how-to-search-for-an-order"
    TITLE = "How to search for an order"
    SCRIPT_NAME = "WAG-1445: Populate How to search for an order guide"
    BREADCRUMB_TITLE = "DAWSON User Guides & Electronic Filing Instructions"

    LOGO_FILENAME = "DAWSON_logo.svg"
    SCALES_ICON_FILENAME = "scales_icon.svg"

    # (key, filename in management/images/dawson, image title, alt text)
    IMAGES = {
        "public": (
            "dawson_order_search_public.png",
            "image of the DAWSON homepage Order tab",
            "The DAWSON homepage with the Order tab selected, showing the Apply "
            "Filters form",
        ),
        "dashboard": (
            "dawson_order_search_practitioner_dashboard.png",
            "image of the DAWSON practitioner dashboard Advanced Search link",
            "A practitioner's DAWSON dashboard with the Advanced Search link in "
            "the upper-right corner highlighted",
        ),
        "advanced": (
            "dawson_order_search_practitioner_advanced.png",
            "image of the DAWSON Advanced Search Order tab",
            "The DAWSON Advanced Search page with the Order tab highlighted",
        ),
        "results": (
            "dawson_order_search_results.png",
            "image of the DAWSON order search results",
            "DAWSON order search results for a Case Title search, with the number "
            "of matches and the results paginator shown",
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
        todays_orders_url = f"{get_environment_specific_dawson_url()}/todays-orders"
        introduction = (
            "<p>An order is a written direction or command issued by a Judge.</p>"
            "<p>Each day's Orders are posted on the U.S. Tax Court website in '"
            f'<a href="{todays_orders_url}">Today\'s Orders</a>'
            "' under 'Orders &amp; Opinions'.</p>"
            "<p>You can search for orders by keyword or phrase. You may also narrow "
            "your search results by docket number, case title/petitioner's name, "
            "judge, or a specific date or date range.</p>"
        )

        phases = [
            self._phase(
                "Access Order Search",
                "<p><b>Petitioner/Public</b></p>"
                "<p>To access Order Search, go to the DAWSON homepage and select "
                "the <b>Order</b> tab.</p>"
                f"{self._embed('public')}"
                "<p><b>Practitioner</b></p>"
                "<p>To access Order Search, log in to your DAWSON account and select "
                "Advanced Search from the upper-right corner of your dashboard. "
                "Then select the <b>Order</b> tab.</p>"
                f"{self._embed('dashboard')}"
                f"{self._embed('advanced')}",
            ),
            self._phase(
                "Search by Keyword, Phrase, Judge, or Date",
                "<p><b>Search by Keyword or Phrase</b></p>"
                "<p>You can search orders using a keyword or phrase. When a keyword "
                "or phrase search is performed, DAWSON searches:</p>"
                "<ul>"
                "<li>The case caption</li>"
                "<li>The content of the order</li>"
                "<li>The order title</li>"
                "</ul>"
                "<p>For exact matches, include quotation marks around the search "
                "term.</p>"
                '<p>Example: "innocent spouse"</p>'
                "<p><b>Refine Your Search Using Connectors</b></p>"
                "<p>You can combine keywords and phrases using connectors.</p>"
                "<p><b>OR ( | )</b></p>"
                "<p>Use the pipe character ( | ) to find orders containing one or "
                "more keywords or phrases.</p>"
                "<p><b>Example</b>: Lien | Levy</p>"
                "<p><b>AND ( + )</b></p>"
                "<p>Use the plus character ( + ) to find orders containing two or "
                "more keywords or phrases.</p>"
                "<p><b>Example</b>: “Motion for Summary Judgment” + "
                '"Denied"</p>'
                "<p><b>Search by Judge or Date</b></p>"
                "<p>To search by judge:</p>"
                "<ul>"
                "<li>Choose a specific judge's name from the drop-down menu.</li>"
                "<li>Note: the default is “All judges”.</li>"
                "</ul>"
                "<p>To search by date:</p>"
                "<ul>"
                "<li>The default is all dates, but you may also choose a custom "
                "range of dates.</li>"
                "<li>When custom dates are selected, you must enter a start date, "
                "but you may choose to leave off the end date.</li>"
                "</ul>",
            ),
            self._phase(
                "Search by Docket Number or Case Title/Petitioner Name",
                "<p>To search orders by docket number:</p>"
                "<ul>"
                "<li>Enter a specific docket number to narrow searches to within a "
                "single Docket number.</li>"
                "</ul>"
                "<p>To search orders by case title or petitioner name:</p>"
                "<ul>"
                "<li>Enter a specific case title or petitioner name in the "
                "appropriate box.</li>"
                "</ul>",
            ),
            self._phase(
                "Review Search Results",
                "<p>After you click <b>Search or hit the enter key on your "
                "keyboard</b>, you will see how many search results are shown. In "
                "the example below, a Case Title search for Smith returned the first "
                "5,000 matches. If the order that you are looking for is not in the "
                "first 5,000 matches, try to refine your search by adding in "
                "additional search criteria (date ranges, a specific judge, etc.)</p>"
                "<p>DAWSON will load 100 results per page. If you would like to view "
                "more results, use the paginator that is located at either the top "
                "of the results or the bottom of the page to see the next 100 "
                "results.</p>"
                f"{self._embed('results')}",
            ),
            self._phase(
                "Tips and Tricks",
                "<p>Searches are not case sensitive.</p>"
                "<p>If there are no matching results, DAWSON will display:</p>"
                '<p><b>"No Matches Found. Check your search terms and try '
                'again."</b></p>'
                "<p>Additional help documentation is available on the Order Search "
                "page.</p>",
                bubble_content="info",
            ),
        ]

        return {
            "title": self.TITLE,
            "show_title": False,
            "introduction": introduction,
            "print_button_text": "Print",
            "show_numbers_in_bubbles": True,
            "phases": phases,
        }

    def _tile(self, title, icon, url):
        return {
            "type": "item",
            "value": {
                "title": title,
                "description": "",
                "icon": {"svg_file": icon.pk},
                "content_alignment": "left",
                "link": [
                    {"type": "external_url", "value": url, "id": str(uuid.uuid4())}
                ],
            },
            "id": str(uuid.uuid4()),
        }

    def _icon(self, filename):
        return self.load_document_from_documents_dir(
            subdirectory=None, filename=filename, title=filename
        )

    def build_resource_cards(self):
        dawson_url = get_environment_specific_dawson_url()
        return [
            {
                "type": "quick_access_tiles",
                "value": {
                    "tiles_hover_enabled": True,
                    "icon_position": "desktop_top_mobile_left",
                    "tiles": [
                        self._tile(
                            "DAWSON", self._icon(self.LOGO_FILENAME), f"{dawson_url}/"
                        ),
                        self._tile(
                            "Today’s Orders",
                            self._icon(self.SCALES_ICON_FILENAME),
                            f"{dawson_url}/todays-orders",
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
        """Create or populate the DAWSON How to search for an order guide."""
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
                "DAWSON How to search for an order page created or updated "
                "successfully."
            )
            script_entry.save()

        except Exception as e:
            logger.error(e)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {e}"
            script_entry.save()
            raise
