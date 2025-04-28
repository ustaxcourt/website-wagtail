from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer


dashboard_images = [
    {
        "title": "image of open cases view",
        "filename": "open-cases.jpg",
    },
    {
        "title": "image of welcome to dawson view",
        "filename": "welcome-to-dawson.jpg",
    },
]


class DashboardPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "dashboard"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Dashboard"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in dashboard_images:
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
                        "value": "Your dashboard is your main landing page once you are signed in to DAWSON.",
                    },
                    {"type": "h2", "value": "Viewing Your Dashboard"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": "Before you file a Petition with the Court, your dashboard will provide information and links to help you with the Petition filing process:",
                                    "image": uploaded_images["welcome-to-dawson.jpg"][
                                        "id"
                                    ],
                                },
                                {
                                    "text": "Helpful Links",
                                    "nested_list": [
                                        {
                                            "list_type": "unordered",
                                            "items": [
                                                {
                                                    "text": "<a href='/efile-a-petition'>How to eFile a Petition</a>",
                                                },
                                                {
                                                    "text": "<a href='/dpt-cities'>Find a Court Location</a>",
                                                },
                                                {
                                                    "text": "<a href='/case-related-forms'>U.S. Tax Court Forms</a>",
                                                },
                                                {
                                                    "text": "<a href='/clinics'>Free Taxpayer Assistance</a>",
                                                },
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "text": "Once you have filed a Petition, you can view all of your cases (open and closed) on your dashboard:",
                                    "image": uploaded_images["open-cases.jpg"]["id"],
                                },
                            ],
                        },
                    },
                    {"type": "h2", "value": "Tips & Tricks"},
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": "To return to your dashboard from anywhere within DAWSON, click <strong>My Cases</strong>.",
                                },
                                {
                                    "text": "Open cases and closed cases are displayed on separate tabs. The number of cases for each is displayed in parentheses.",
                                },
                                {
                                    "text": "The default display is 20 cases. To view more, click the <strong>Load More</strong> button.",
                                },
                                {
                                    "text": "It is typical for a self-represented (pro se) petitioner to have just one case.",
                                },
                            ],
                        },
                    },
                ],
                search_description="View and manage your DAWSON dashboard",
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
