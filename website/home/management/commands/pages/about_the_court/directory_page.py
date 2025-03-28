from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import DirectoryIndex


class DirectoryPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "directory"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Directory"

        _ = [
            {
                "title": "Office of the Clerk of the Court",
                "detail": "The Clerk's Office is responsible for, among other things, the business management and operations of the Court. General procedure questions can be directed here.",
                "phone_number": "(202) 521-0700",
            },
            {
                "title": "Request for Tax Court Rules of Practice and Procedure",
                "detail": "Tax Court Rules of Practice and Procedure are also available online.",
                "phone_number": "(202) 521-0700",
            },
            {
                "title": "Admissions",
                "detail": "Admissions procedures for practice before the Tax Court and practitioner access for DAWSON.",
                "phone_number": "(202) 521-4629",
            },
        ]

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return
        self.logger.write(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=DirectoryIndex(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                body=[
                    {
                        "type": "entries",
                    }
                ],
            )
        )
        new_page.save()
