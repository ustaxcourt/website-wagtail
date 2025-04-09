from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer


find_opinion_images = [
    {
        "title": "DAWSON Search Image - Public Access",
        "filename": "find-opinion.jpg",
    },
    {
        "title": "DAWSON Search Image - Practitioner Access",
        "filename": "advanced-search.jpg",
    },
    {
        "title": "DAWSON Search Image - Opinion Tab",
        "filename": "opinion-search.jpg",
    },
    {
        "title": "DAWSON Search Image - Search Results",
        "filename": "opinion-results.jpg",
    },
]


class DawsonFindAnOpinionPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "find-an-opinion"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Find an Opinion"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in find_opinion_images:
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
                        "value": "An opinion is the written determination of a Judge on the issues tried and submitted to the Court for decision. Each day's opinions are posted on the Court's website, <strong><a href='https://www.ustaxcourt.gov/'>www.ustaxcourt.gov</a></strong>, in 'Today's Opinions' under 'Orders & Opinions'. If you need to search for an opinion, you can search by a keyword or phrase. In addition, you may narrow your search results by adding in a specific Docket Number, Case Title/Petitioner's name, the Judge who issued the Opinion, or by including a specific date or date range. You may also filter by opinion type.",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "The steps to access Opinion Search depends on the role you have in DAWSON.",
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
                                    "text": "Click the <strong>Opinion tab</strong>",
                                    "image": uploaded_images["find-opinion.jpg"]["id"],
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
                                    "text": "Click on the <strong>Opinion Tab</strong>",
                                    "image": uploaded_images["opinion-search.jpg"][
                                        "id"
                                    ],
                                },
                            ],
                        },
                    },
                    {"type": "hr", "value": True},
                    {"type": "h2", "value": "How to Find an Opinion"},
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
                                                                    "text": "The content of the opinion"
                                                                },
                                                                {
                                                                    "text": "The opinion title"
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
                                                                    "text": 'For example: Search <strong>"Premium Tax Credit"</strong> for results containing that exact phrase.'
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
                                                                                    "text": 'For example: Search <strong>"fraud" | "sanctions"</strong>.'
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
                                                                                    "text": 'For example: Search<strong> "in-kind + "distribution" + "IRA"</strong>'
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
                                    "text": "To search opinions by Docket Number:",
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
                                    "text": "To search opinions by Case title or Petitioner name:",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "Enter a specific Case title or Petitioner name to search for."
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
                                                    "text": "Enter a specific Judge's name."
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
                                    "text": "To search by Opinion Type:",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "All opinion type checkboxes are selected by default."
                                                },
                                                {
                                                    "text": "Uncheck the opinion types so that only the opinion types that you want to search for are left checked."
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
                                                    "text": "After you click <strong>Search or hit the enter key on your keyboard</strong>, you will see how many search results are shown. In the example below, a keyword search for Smith returned the first 100 matches. If the opinion that you are looking for is not in the first 100 matches, try to refine your search by adding in additional search criteria (date ranges, a specific Judge, etc.)."
                                                },
                                                {
                                                    "text": "DAWSON will only load the first 25 results on the page. If you would like to view more results than what initially is displayed, scroll to the bottom of the page and click <strong>Load more</strong>.",
                                                    "image": uploaded_images[
                                                        "opinion-results.jpg"
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
                                    "text": "Additional help documentation is available on the DAWSON Opinion search page if needed."
                                },
                            ],
                        },
                    },
                ],
                search_description="Learn how to find and search for opinions in DAWSON",
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
