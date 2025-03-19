from home.management.commands.pages.page_initializer import PageInitializer
from home.models import Footer


class FooterInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        settings = Footer.objects.all().first()

        if settings:
            self.logger.write("- Footer settings already exists.")
            return

        if not settings:
            Footer.objects.create(
                technicalQuestions=(
                    "For assistance with DAWSON, view the FAQs and other materials "
                    '<a href="/faqs" target="_blank">here</a>. '
                    "To contact the Webmaster for technical issues or problems with the website, "
                    'send an email to <a href="mailto:webmaster@ustaxcourt.gov">webmaster@ustaxcourt.gov</a>. '
                    "No documents can be filed with the Court at this email address."
                ),
                otherQuestions="For all non-technical questions, contact the Office of the Clerk of the Court at (202) 521-0700.",
            )
            self.logger.write("Successfully created Footer settings.")

    def update(self):
        settings = Footer.objects.all().first()

        if settings:
            self.logger.write("- Footer settings already exists. Updating.")
        else:
            self.logger.write("- Can't find Footer settings. STOPPING.")
            return

        footer = Footer.objects.first()
        footer.technicalQuestions = (
            "For assistance with DAWSON, view the FAQs and other materials "
            '<a href="/dawson">here</a>. '
            "To contact the Webmaster for technical issues or problems with the website, "
            'send an email to <a href="mailto:webmaster@ustaxcourt.gov">webmaster@ustaxcourt.gov</a>. '
            "No documents can be filed with the Court at this email address."
        )
        footer.otherQuestions = """For all non-technical questions, contact the Office of the Clerk of the Court at <a href="tel:+12025210700">(202) 521-0700</a>."""
        footer.save()
        self.logger.write("Successfully updated Footer settings.")
