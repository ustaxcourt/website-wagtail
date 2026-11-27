import logging
import uuid

from wagtail.models import Page
from wagtail.images import get_image_model

from home.management.commands.pages.page_initializer import PageInitializer
from home.models.pages.petitioner_experience import PetitionerExperiencePage
from home.models.utils.execute_script import ExecuteScript
from search.dawson_client import get_environment_specific_dawson_url

logger = logging.getLogger(__name__)

PAGE_SLUG = "dawson-how-to-search-for-an-opinion"
PAGE_TITLE = "How to search for an opinion"
SCRIPT_NAME = "WAG-1446: Populate How to search for an opinion user guide"
CONTENT_SCRIPT_NAME = (
    "WAG-1446: Keep only the opinion results screenshot in the opinion guide"
)
ACCESS_IMAGES_SCRIPT_NAME = (
    "WAG-1446: Add the Access Opinion Search screenshots to the opinion guide"
)
RESOURCES_SCRIPT_NAME = "WAG-1446: Add resource cards to the opinion guide"
RESOURCE_ICON_FILENAME = "DAWSON_icon.svg"
BREADCRUMB_TITLE = "DAWSON User Guides & Electronic Filing Instructions"
IMAGE_FILENAME = "opinion-limited-search.png"
IMAGE_TITLE = "DAWSON Opinion Limited Search"
IMAGE_ALT = "DAWSON Opinion search results showing the 5,000 result limit."
PUBLIC_IMAGE_FILENAME = "opinion-search-public.jpg"
PUBLIC_IMAGE_TITLE = "DAWSON Opinion Search Public"
PUBLIC_IMAGE_ALT = (
    "DAWSON homepage Search page with the Opinion tab selected and an arrow "
    "pointing to it."
)
PRACTITIONER_IMAGE_FILENAME = "practitioner-advanced-search.jpg"
PRACTITIONER_IMAGE_TITLE = "DAWSON Practitioner Advanced Search"
PRACTITIONER_IMAGE_ALT = (
    "Practitioner dashboard with an arrow pointing to the Advanced Search link "
    "in the Search for a Case panel."
)
PRACTITIONER_OPINION_IMAGE_FILENAME = "opinion-search-practitioner.png"
PRACTITIONER_OPINION_IMAGE_TITLE = "DAWSON Opinion Search Practitioner"
PRACTITIONER_OPINION_IMAGE_ALT = (
    "DAWSON Search page for a logged-in practitioner with the Opinion tab selected."
)


def _image_embed(image_id, alt=IMAGE_ALT):
    return f'<embed alt="{alt}" embedtype="image" format="fullwidth" id="{image_id}"/>'


def _heading(text):
    return f"<p><strong>{text}</strong></p>"


def _bullets(*items):
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def _phase(title, instructions, bubble_content="number"):
    return {
        "type": "phase",
        "value": {
            "title": title,
            "bubble_content": bubble_content,
            "instructions": instructions,
            "your_tasks": [],
            "helpful_information": [],
        },
    }


class DawsonHowToSearchForAnOpinion(PageInitializer):
    def get_image(self, filename, title):
        image = get_image_model().objects.filter(title=title).first()
        if image is None:
            image = self.load_image_from_images_dir("dawson", filename, title)
        if image is None:
            raise FileNotFoundError(f"Opinion guide image not found: {filename}")
        return image

    def build_resource_cards(self):
        dawson_url = get_environment_specific_dawson_url()
        icon = self.load_document_from_documents_dir(
            subdirectory=None,
            filename=RESOURCE_ICON_FILENAME,
            title=RESOURCE_ICON_FILENAME,
        )
        resources = [
            ("DAWSON", dawson_url),
            ("Today's Opinions", f"{dawson_url}/todays-opinions"),
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
                        for title, url in resources
                    ],
                },
                "id": str(uuid.uuid4()),
            }
        ]

    def add_resource_cards(self):
        """Adds the Resources column to a guide created before it existed."""
        page = PetitionerExperiencePage.objects.filter(slug=PAGE_SLUG).first()
        if page is None:
            raise Page.DoesNotExist(
                f"Page '{PAGE_SLUG}' not found; cannot add its resource cards."
            )
        if page.resource_cards:
            logger.info("Page '%s' already has resource cards.", PAGE_SLUG)
            return

        page.resource_cards = self.build_resource_cards()
        page.save_revision().publish()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        user_guides_page = Page.objects.get(slug="dawson-user-guides")
        fields = {
            "title": PAGE_TITLE,
            "slug": PAGE_SLUG,
            "seo_title": PAGE_TITLE,
            "search_description": PAGE_TITLE,
            "navigation_ribbon": None,
            "show_floating_definitions_button": True,
            "introductory_text": "",
            "breadcrumb": [
                {
                    "type": "breadcrumb",
                    "value": {
                        "breadcrumb_title": BREADCRUMB_TITLE,
                        "breadcrumb_page": [
                            {"type": "internal_page", "value": user_guides_page.id}
                        ],
                    },
                }
            ],
            "body": [{"type": "detailed_timeline", "value": self.build_timeline()}],
            "resource_cards": self.build_resource_cards(),
        }

        existing_page = Page.objects.filter(slug=PAGE_SLUG).first()
        if existing_page:
            page = existing_page.specific
            if not isinstance(page, PetitionerExperiencePage):
                raise TypeError(
                    f"Page '{PAGE_SLUG}' must be a Petitioner Experience page."
                )
            if page.body:
                logger.info(
                    "Page '%s' already has body content; leaving it unchanged.",
                    PAGE_SLUG,
                )
                return

            for field_name, value in fields.items():
                setattr(page, field_name, value)
            logger.info("Populating the existing '%s' page.", PAGE_TITLE)
        else:
            page = home_page.add_child(instance=PetitionerExperiencePage(**fields))
            logger.info("Creating the '%s' page.", PAGE_TITLE)

        page.save_revision().publish()

    def build_timeline(self):
        dawson_url = get_environment_specific_dawson_url()
        todays_opinions_url = f"{dawson_url}/todays-opinions"
        image_embed = _image_embed(self.get_image(IMAGE_FILENAME, IMAGE_TITLE).id)
        public_image_embed = _image_embed(
            self.get_image(PUBLIC_IMAGE_FILENAME, PUBLIC_IMAGE_TITLE).id,
            PUBLIC_IMAGE_ALT,
        )
        practitioner_opinion_image_embed = _image_embed(
            self.get_image(
                PRACTITIONER_OPINION_IMAGE_FILENAME, PRACTITIONER_OPINION_IMAGE_TITLE
            ).id,
            PRACTITIONER_OPINION_IMAGE_ALT,
        )
        practitioner_image_embed = _image_embed(
            self.get_image(PRACTITIONER_IMAGE_FILENAME, PRACTITIONER_IMAGE_TITLE).id,
            PRACTITIONER_IMAGE_ALT,
        )
        search_phrase_bullets = _bullets(
            "The case caption", "The content of the opinion", "The opinion title"
        )
        judge_bullets = _bullets(
            "Enter a specific judge's name.",
            'Note: the default is "All judges".',
        )
        date_bullets = _bullets(
            "The default is all dates, but you may also choose a custom range of "
            "dates.",
            "When custom dates are selected, you must enter a start date, but you "
            "may choose to leave off the end date.",
        )
        opinion_type_bullets = _bullets(
            "All opinion type checkboxes are selected by default.",
            "Uncheck the opinion types so that only the opinion types that you "
            "want to search for are left checked.",
        )
        docket_bullets = _bullets(
            "Enter a specific docket number to narrow searches to within a single "
            "docket number."
        )
        case_title_bullets = _bullets(
            "Enter a specific case title or petitioner name to search for."
        )

        return {
            "title": PAGE_TITLE,
            "show_title": False,
            "print_button_text": "Print",
            "show_numbers_in_bubbles": True,
            "introduction": (
                "<p>An opinion is the written determination of a judge on the issues "
                "tried and submitted to the Court for decision.<br/>"
                "Each day's Opinions are posted on the United States Tax Court "
                f"website under '<a href=\"{todays_opinions_url}\">Today's "
                "Opinions</a>' under 'Orders &amp; Opinions'.<br/>"
                "You can search for opinions by keyword or phrase. You may also "
                "narrow your search results by docket number, case "
                "title/petitioner's name, judge, date, or opinion type.</p>"
            ),
            "phases": [
                _phase(
                    "Access Opinion Search",
                    f"{_heading('Petitioner/Public')}"
                    "<p>To access Opinion Search, go to the "
                    f'<a href="{dawson_url}">DAWSON homepage</a> and select the '
                    "<strong>Opinion</strong> tab.</p>"
                    f"{public_image_embed}"
                    f"{_heading('Practitioner')}"
                    "<p>To access Opinion Search, log in to your DAWSON account and "
                    "select <strong>Advanced Search</strong> from the upper-right "
                    "corner of your dashboard. Then select the "
                    "<strong>Opinion</strong> tab.</p>"
                    f"{practitioner_image_embed}"
                    f"{practitioner_opinion_image_embed}",
                ),
                _phase(
                    "Search by Keyword, Phrase, Judge, Date, or Opinion Type",
                    f"{_heading('Search by Keyword or Phrase')}"
                    "<p>You can search opinions using a keyword or phrase. When a "
                    "search is initiated from the keyword or phrase field, DAWSON "
                    "searches:</p>"
                    f"{search_phrase_bullets}"
                    "<p>For exact matches, include quotation marks around your "
                    "search term.<br/>"
                    'Example: <strong>"Premium Tax Credit"</strong><br/>'
                    "Do not use quotation marks if you do not want an exact "
                    "match.<br/>"
                    "Example: Searching for <strong>Smith</strong> may return "
                    "results containing <strong>Smith</strong> as well as "
                    "<strong>Smithson</strong>.</p>"
                    f"{_heading('Refine Your Search Using Connectors')}"
                    "<p>You can use connectors in combination with keyword and "
                    "phrase searches.</p>"
                    f"{_heading('OR ( | )')}"
                    "<p>Use the pipe character ( | ) to find opinions containing "
                    "one or more keywords or phrases.<br/>"
                    '<strong>Example:</strong> "fraud" | "sanctions"<br/>'
                    "The pipe character ( | ) is usually located above the "
                    "backslash ( \\ ) on your keyboard.</p>"
                    f"{_heading('AND ( + )')}"
                    "<p>Use the plus character ( + ) to find opinions containing "
                    "two or more keywords or phrases.<br/>"
                    '<strong>Example:</strong> "in-kind" + "distribution" + "IRA"</p>'
                    f"{_heading('Search by Judge, Date or Opinion Type')}"
                    "<p>To search by judge:</p>"
                    f"{judge_bullets}"
                    "<p>To search by date:</p>"
                    f"{date_bullets}"
                    "<p>To search by opinion type:</p>"
                    f"{opinion_type_bullets}",
                ),
                _phase(
                    "Search by Docket Number or Case Title/Petitioner Name",
                    "<p>To search opinions by docket number:</p>"
                    f"{docket_bullets}"
                    "<p>To search opinions by case title or petitioner name:</p>"
                    f"{case_title_bullets}",
                ),
                _phase(
                    "Review Search Results",
                    "<p>After you click <strong>Search or hit the enter key on your "
                    "keyboard</strong>, you will see how many search results are "
                    "shown. In the example below, a keyword search for Smith "
                    "returned the first 5,000 matches. If the opinion that you are "
                    "looking for is not in the first 5,000 matches, try to refine "
                    "your search by adding in additional search criteria (date "
                    "ranges, a specific judge, etc.).</p>"
                    "<p>DAWSON will load 100 results per page. If you would like to "
                    "view more results, use the paginator that is located at either "
                    "the top of the results or the bottom of the page to see the "
                    "next 100 results.</p>"
                    f"{image_embed}",
                ),
                _phase(
                    "Tips and Tricks",
                    "<p>Searches are not case sensitive.</p>"
                    "<p>If there are no matching results, DAWSON will display:<br/>"
                    '<strong>"No Matches Found. Check your search terms and '
                    'try again."</strong></p>'
                    "<p>Additional help documentation is available on the Opinion "
                    "Search page.</p>",
                    bubble_content="info",
                ),
            ],
        }

    def update_timeline_content(self):
        page = Page.objects.filter(slug=PAGE_SLUG).first()
        if page is None:
            raise Page.DoesNotExist(
                f"Page '{PAGE_SLUG}' not found; cannot update its content."
            )

        page = page.specific
        if not isinstance(page, PetitionerExperiencePage):
            raise TypeError(f"Page '{PAGE_SLUG}' must be a Petitioner Experience page.")

        body = page.body.get_prep_value()
        timeline = next(
            (block for block in body if block["type"] == "detailed_timeline"), None
        )
        if timeline is None:
            body.append({"type": "detailed_timeline", "value": self.build_timeline()})
        else:
            timeline["value"] = self.build_timeline()

        page.body = body
        page.save_revision().publish()
        logger.info("Updated '%s' content to match the expanded design.", PAGE_TITLE)

    def run(self):
        if not Page.objects.filter(slug="dawson-user-guides").exists():
            raise Page.DoesNotExist(
                f"'dawson-user-guides' page not found; cannot run '{SCRIPT_NAME}'."
            )

        existing_page = Page.objects.filter(slug=PAGE_SLUG).first()
        if existing_page and existing_page.has_unpublished_changes:
            logger.warning(
                "Page '%s' has unpublished changes; deferring initializer updates.",
                PAGE_SLUG,
            )
            return 0

        created = self._run_once(SCRIPT_NAME, self.create)
        content_updated = self._run_once(
            CONTENT_SCRIPT_NAME, self.update_timeline_content
        )
        images_updated = self._run_once(
            ACCESS_IMAGES_SCRIPT_NAME, self.update_timeline_content
        )
        resources_added = self._run_once(RESOURCES_SCRIPT_NAME, self.add_resource_cards)
        if not (created or content_updated or images_updated or resources_added):
            return 0

    def _run_once(self, command_name, action):
        if ExecuteScript.command_exists(command_name):
            logger.info("Script '%s' already exists. Skipping.", command_name)
            return False

        script_entry = ExecuteScript.create_script(command_name)
        try:
            action()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = f"{command_name} completed successfully."
            script_entry.save()
        except Exception as error:
            logger.exception(
                "Could not run DAWSON opinion guide script '%s'.", command_name
            )
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error}"
            script_entry.save()
            raise
        return True
