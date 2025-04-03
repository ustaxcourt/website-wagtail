from wagtail.models import Page
from home.models import EnhancedRawHTMLPage
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
            instance=EnhancedRawHTMLPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="View and manage your DAWSON dashboard",
                raw_html_body=[
                    {
                        "type": "raw_html",
                        "value": """
<div id='dashboard-page'>
<p>Your dashboard is your main landing page once you are signed in to DAWSON.</p>

<h2>Viewing Your Dashboard</h2>

<ol>
    <li>Before you file a Petition with the Court, your dashboard will provide information and links to help you with the Petition filing process:</li>
</ol>

<img src="{welcome_image_url}" alt="Welcome to DAWSON dashboard view">

<ol start="2">
    <li>Helpful Links</li>
    <ul>
        <li><strong><a href="/petitioners-start">How to eFile a Petition</a></strong></li>
        <li><strong><a href="/dpt_cities.html">Find a Court Location</a></strong></li>
        <li><strong><a href="/case-related-forms">U.S. Tax Court Forms</a></strong></li>
        <li><strong><a href="/clinics">Free Taxpayer Assistance</a></strong></li>
    </ul>
</ol>

<ol start="3">
    <li>Once you have <strong><a href="/petitioners-start">filed a Petition</a></strong>, you can view all of your cases (open and closed) on your dashboard:</li>
</ol>

<img src="{cases_image_url}" alt="Open cases dashboard view">

<h3>Tips & Tricks</h3>

<ul>
    <li>To return to your dashboard from anywhere within DAWSON, click <strong>My Cases</strong>.</li>
    <li>Open cases and closed cases are displayed on separate tabs. The number of cases for each is displayed in parentheses.</li>
    <li>The default display is 20 cases. To view more, click the <strong>Load More</strong> button.</li>
    <li>It is typical for a self-represented (pro se) petitioner to have just one case.</li>
</ul>
</div>
""".format(
                            welcome_image_url=uploaded_images["welcome-to-dawson.jpg"][
                                "url"
                            ],
                            cases_image_url=uploaded_images["open-cases.jpg"]["url"],
                        ),
                    },
                ],
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
