from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer


page_images = [
    {
        "title": "image of find a case view",
        "filename": "find-a-case.jpg",
    },
]


class FindACasePageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "find-a-case"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Find a Case"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        uploaded_images = {}

        for image in page_images:
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
                        "value": "To search for a case in <a href='https://dawson.ustaxcourt.gov/'>DAWSON</a>, go to the DAWSON homepage. You can search for a case by <a href='#NAME'>Petitioner Name</a> or <a href='#DOCKET'>Docket Number</a> on the Case tab.",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "image",
                        "value": uploaded_images["find-a-case.jpg"]["id"],
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "heading",
                        "value": {
                            "level": "h2",
                            "text": "Search by Docket Number",
                            "id": "DOCKET",
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": """
<ol>
<li>Go to the <a href='https://dawson.ustaxcourt.gov/'>DAWSON homepage</a>.</li>
<li>To search for a case by Docket Number, you must include the dash in the Docket Number (e.g., 123-18).</li>
<li>You may, but do not have to, include the letter suffix (S, L, SL, R, X, D, or P) of the Docket Number to find a case.</li>
<li>When you enter a Docket Number that matches a case in the system, that case will display. If you enter a Docket Number that has no matching case, you will get a “No Matches Found” message.</li>
</ol>
                     """,
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "heading",
                        "value": {
                            "level": "h2",
                            "text": "Search by Name",
                            "id": "NAME",
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": """
<ol>
<li>Go to the <a href='https://dawson.ustaxcourt.gov/'>DAWSON homepage</a>.</li>
<li>To search for a case by petitioner name, you must enter the petitionerʼs full or last name. Partial name searches (e.g., entering “Ron” for Ronald) are not currently supported.</li>
<li>You can improve your search results by filtering the Country, State, Date filed start date, Date filed end date, Case procedure, or Case type (i.e. docket suffix) to further refine your search. If the United States is selected, U.S. Territories and military bases are included. These fields are not required but can be used in any combination to refine results.</li>
</ol>
                     """,
                    },
                ],
                search_description="Find a case in DAWSON",
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
