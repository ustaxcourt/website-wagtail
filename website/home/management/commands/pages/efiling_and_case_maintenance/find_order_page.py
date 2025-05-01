from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)


find_order_images = [
    {
        "title": "DAWSON Search Image - Public Access",
        "filename": "find-order.jpg",
    },
    {
        "title": "DAWSON Search Image - Practitioner Access",
        "filename": "advanced-search.jpg",
    },
    {
        "title": "DAWSON Search Image - Order Tab",
        "filename": "order-search.jpg",
    },
    {
        "title": "DAWSON Search Image - Search Results",
        "filename": "order-results.jpg",
    },
]


class DawsonFindAnOrderPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "find-an-order"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Find an Order"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in find_order_images:
            image_uploaded = self.load_image_from_images_dir(
                "dawson", image["filename"], image["title"]
            )

            if image_uploaded:
                uploaded_images[image["filename"]] = {
                    "id": image_uploaded.id,
                    "url": image_uploaded.file.url,
                }

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": "An Order is a written direction or command issued by a Judge. Each day's Orders are posted on the Court's website, <strong><a href='https://www.ustaxcourt.gov/'>www.ustaxcourt.gov</a></strong>, under '<strong><a href='https://dawson.ustaxcourt.gov/todays-orders' target='_blank'>Today's Orders</a></strong>' in 'Orders & Opinions'. To search for an order, you can search by a keyword or phrase. In addition, you may also narrow your search results by adding in a specific Docket number, Case Title/Petitioner's name, the Judge who issued the order, or by including a specific date or date range.",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "The steps to access Order Search depends on the role you have in DAWSON.",
                    },
                    {"type": "h2", "value": "Petitioners/Public"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": "Go to <strong><a href='https://dawson.ustaxcourt.gov/' target='_blank'>https://dawson.ustaxcourt.gov/</a></strong>",
                                },
                                {
                                    "text": "Click the <strong>Order tab</strong>",
                                    "image": uploaded_images["find-order.jpg"]["id"],
                                },
                            ],
                        },
                    },
                    {"type": "h2", "value": "Practitioners"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": "Log in to your DAWSON account",
                                },
                                {
                                    "text": "Click on the <strong>Advanced Search</strong> URL in the upper right corner of your dashboard.",
                                    "image": uploaded_images["advanced-search.jpg"][
                                        "id"
                                    ],
                                },
                                {
                                    "text": "Click on the <strong>Order Tab</strong>",
                                    "image": uploaded_images["order-search.jpg"]["id"],
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "h2", "value": "How to Find an Order"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {
                                    "text": "Search orders with a keyword or phrase",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "When search is initiated from the keyword or phase area, DAWSON will include in the search:",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "unordered",
                                                            "items": [
                                                                {
                                                                    "text": "The case caption"
                                                                },
                                                                {
                                                                    "text": "The content of the order"
                                                                },
                                                                {
                                                                    "text": "The order title"
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                                {
                                                    "text": "For exact matches, be sure to include quotation marks around your search term.",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "unordered",
                                                            "items": [
                                                                {
                                                                    "text": 'For example: Search <strong>"innocent spouse"</strong> for results containing that exact phrase.'
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                                {
                                                    "text": "Do not enter quotation marks for searches that you do not want exact matches for.",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "unordered",
                                                            "items": [
                                                                {
                                                                    "text": "For example: If you enter <strong>Smith</strong> for your search, results will include terms that include <strong>Smith</strong>, as well as <strong>Smithson</strong>."
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "text": "Use Connectors ( | , + ) with keywords/phrases.",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "You can use connectors in combination with the exact keyword or phrase search.",
                                                    "nested_list": [
                                                        {
                                                            "list_type": "unordered",
                                                            "items": [
                                                                {
                                                                    "text": "<strong>OR (|)</strong>",
                                                                    "nested_list": [
                                                                        {
                                                                            "list_type": "unordered",
                                                                            "items": [
                                                                                {
                                                                                    "text": "Use the | (pipe character) to find documents containing one or more of the keywords or phrases."
                                                                                },
                                                                                {
                                                                                    "text": "The pipe character (|) is usually located above the backslash (\\) on your keyboard."
                                                                                },
                                                                                {
                                                                                    "text": "For example: Search <strong>Lien | Levy</strong>."
                                                                                },
                                                                            ],
                                                                        },
                                                                    ],
                                                                },
                                                                {
                                                                    "text": "<strong>AND (+)</strong>",
                                                                    "nested_list": [
                                                                        {
                                                                            "list_type": "unordered",
                                                                            "items": [
                                                                                {
                                                                                    "text": "Use the + (plus character) to find documents two or more keywords or phrases"
                                                                                },
                                                                                {
                                                                                    "text": 'For example: Search<strong> Motion for Summary Judgment + "Denied"</strong>'
                                                                                },
                                                                            ],
                                                                        },
                                                                    ],
                                                                },
                                                            ],
                                                        },
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "text": "To search orders by Docket Number:",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "Enter a specific Docket Number to narrow searches to within a single Docket number."
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "text": "To search orders by Case title or Petitioner name:",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "Enter a specific Case title or Petitioner name in the appropriate box."
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "text": "To search by Judge:",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "Choose a specific Judge's Name from the drop-down menu."
                                                },
                                                {
                                                    "text": "Note: the default is all Judges."
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "text": "To search by date:",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "The default is all dates, but you may also choose a custom range of dates."
                                                },
                                                {
                                                    "text": "When custom dates are selected, you must enter a start date, but you may choose to leave off the end date."
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "text": "Total Results",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "After you click <strong>Search or hit the enter key on your keyboard</strong>, you will see how many search results are shown. In the example below, a Case Title search for Jones returned the first 100 matches. If the Order that you are looking for is not in the first 100 matches, try to refine your search by adding in additional search criteria (date ranges, a specific Judge, etc.)"
                                                },
                                                {
                                                    "text": "DAWSON will only load the first 25 results on the page. If you would like to view more results than what initially is displayed, scroll to the bottom of the page and click <strong>Load more</strong>.",
                                                    "image": uploaded_images[
                                                        "order-results.jpg"
                                                    ]["id"],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "h2", "value": "Tips & Tricks"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "unordered",
                            "items": [
                                {"text": "Search is NOT case sensitive."},
                                {
                                    "text": "If there are no matches, you will receive a message that states <strong>'No Matches Found. Check your search terms and try again.'</strong>"
                                },
                                {
                                    "text": "Additional help documentation is available on the DAWSON Order search page if needed."
                                },
                            ],
                        },
                    },
                ],
                search_description="Learn how to find and search for orders in DAWSON",
            )
        )

        new_page.save_revision().publish()
        logger.info(f"Successfully created the '{title}' page.")
