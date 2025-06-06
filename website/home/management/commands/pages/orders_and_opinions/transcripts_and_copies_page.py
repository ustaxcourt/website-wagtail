from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)


class TranscriptsAndCopiesPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "transcripts-and-copies"
        title = "Transcripts & Copies"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        body_text = (
            "<strong>Transcripts</strong><br>"
            "<p>Transcripts of proceedings before the Tax Court are supplied to the parties and to the public by the official reporter at such rates as may be fixed by contract "
            'between the Court and the reporter. Transcripts may be ordered directly from the official reporter, <a href="https://www.escribers.net/" target="_blank" rel="noopener noreferrer">eScribers</a>, by submitting a '
            '<a href="https://gateway.escribers.net/newportal/home/ordertranscriptform/340" target="_blank" rel="noopener noreferrer">Transcript Order Form</a> or by calling <a href="tel:+18002570885">800-257-0885</a> ext. 7. You can also send an email to '
            '<a href="mailto:reportingsales@escribers.net">reportingsales@escribers.net</a>.</p>'
            '<p>Transcripts are not viewable even to the parties through <a href="https://dawson.ustaxcourt.gov/">DAWSON</a> until 90 days after the date of the trial (or hearing). Transcripts are available as a copy '
            "request after 90 days.</p>"
            "<strong>Copies</strong><br>"
            "<p>Requests for copies of Court records from non-parties (copy requests) may be made in person or by telephone and will be fulfilled electronically by email. The "
            'Court\'s fees with respect to these copy requests will be $0.50 per page, with a per-document cap of $3.00. The Records Department can be reached at <a href="tel:+12025214688">202-521-4688</a>.</p>'
            "<p>Litigants with active cases who are registered for electronic access may electronically file, view, and print at home documents in their cases without charge. "
            'Register for DAWSON by following the <a href="/dawson">Register for DAWSON instructions</a>.</p>'
        )

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Information about obtaining transcripts and copies of Tax Court documents",
                body=[
                    {"type": "paragraph", "value": body_text},
                ],
            )
        )

        logger.info(f"Successfully created the '{title}' page.")
