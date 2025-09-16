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
                    "For assistance with DAWSON, the Court's Electronic Filing and Case Management System, "
                    "refer to the "
                    '<a href="/dawson">DAWSON</a> page or email '
                    '<a href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"> dawson.support@ustaxcourt.gov</a>.<br>'
                    '<span class="spacing-fix"> </span>'
                    "Be sure to include your case docket number in your email. For all other questions contact the Office of the Clerk of Court at "
                    '(<a style="text-decoration: underline;" href="tel:+2025210700">202) 521-0700</a></span>.'
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
            "For assistance with DAWSON, the Court's Electronic Filing and Case Management System, "
            "refer to the "
            '<a href="/dawson">DAWSON</a> page or email '
            '<a href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"> dawson.support@ustaxcourt.gov</a>.<br>'
            '<span class="spacing-fix"> </span>'
            "Be sure to include your case docket number in your email. For all other questions contact the Office of the Clerk of Court at "
            '(<a style="text-decoration: underline;" href="tel:+2025210700">202) 521-0700</a></span>.'
        )
        footer.otherQuestions = """For all non-technical questions, contact the Office of the Clerk of the Court at <a href="tel:+12025210700">(202) 521-0700</a>."""
        footer.save()
        logger.info("Successfully updated Footer settings.")
