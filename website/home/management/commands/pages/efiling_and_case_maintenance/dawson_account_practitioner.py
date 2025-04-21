from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer


class DawsonAccountPractitionerPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "dawson-account-practitioner"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "How to Get a DAWSON Account: Practitioners"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": """The Court will create DAWSON accounts for practitioners.
                        <ul>
                            <li>Practitioners with eAccess credentials who did not receive temporary DAWSON credentials, or did not activate them before they expired, should contact  <a href="mailto:dawson.support@ustaxcourt.gov" title="Contact DAWSON support">dawson.support@ustaxcourt.gov</a> to request new temporary DAWSON credentials.</li>
                            <li>Practitioners who did not previously register for eAccess and would like to register for DAWSON should contact <a href="mailto:dawson.support@ustaxcourt.gov" title="Contact DAWSON support">dawson.support@ustaxcourt.gov</a>.</li>
                            <li>Practitioners who would like to apply for admission to practice before the U.S. Tax Court can find the application and instructions <a href="/practitioners" title="Guidance for Practitioners
">here</a>. DAWSON access will be provided to successful applicants with their other admissions materials.</li>
                        </ul>
                        """,
                    },
                ],
                search_description=title,
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
