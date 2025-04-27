from home.management.commands.pages.page_initializer import PageInitializer
from home.models import Footer
import logging

logger = logging.getLogger(__name__)


class FooterInitializer(PageInitializer):
    def create(self):
        settings = Footer.objects.all().first()

        if settings:
            logger.info("- Footer settings already exists.")
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
            logger.info("Successfully created Footer settings.")

    def update(self):
        settings = Footer.objects.all().first()

        if settings:
            logger.info("- Footer settings already exists. Updating.")
        else:
            logger.warning("- Can't find Footer settings. STOPPING.")
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
        logger.info("Successfully updated Footer settings.")
