from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, CommonText
import logging

logger = logging.getLogger(__name__)


docs = {
    "clinics.pdf": "",
}


class ClinicsProBonoProgramsPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "clinics"
        title = "Clinics & Pro Bono Programs"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for document in docs.keys():
            uploaded_document = self.load_document_from_documents_dir(None, document)
            docs[document] = uploaded_document.file.url

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title="Clinical, Student Practice & Bar Sponsored Calendar Call Program",
                search_description="Clinical, Student Practice & Bar Sponsored Calendar Call Program",
                body=[
                    {
                        "type": "h2",
                        "value": "Requirements for Participation in the United States Tax Court Clinical, Student Practice & Bar Sponsored Calendar Call Program",
                    },
                    {
                        "type": "paragraph",
                        "value": f'Tax clinics and Bar sponsored calendar call programs provide important advice and assistance to many low income, self represented taxpayers who have disputes with the Internal Revenue Service. The <strong><a href="{docs["clinics.pdf"]}" target="_blank" title="participating clinics">participating clinics</a></strong> listed are not part of the Internal Revenue Service or the Tax Court. The Tax Court does not endorse or recommend any particular tax clinic or Bar sponsored calendar call program.',
                    },
                    {
                        "type": "paragraph",
                        "value": 'The United States Tax Court includes on its Web site requirements for academic law school clinics (“<strong><a href="/clinics-academic">U.S. Tax Court Requirements for Academic Clinics (Law School)</a></strong>”), non law school academic clinics ("<strong><a href="/clinics-academic-non-law-school">U.S. Tax Court Requirements for Academic Clinics (Non Law School)</a></strong>") and nonacademic clinics (“<strong><a href="/clinics-nonacademic">U.S. Tax Court Requirements for Nonacademic Clinics</a></strong>”). The Court also includes on its Web site requirements for Bar sponsored calendar call programs (“<strong><a href="/clinics-calendar-call">U.S. Tax Court Requirements for Bar Sponsored Calendar Call Programs</a></strong>”), and the student practice program sponsored by the Office of Chief Counsel of the Internal Revenue Service (“<strong><a href="/clinics-chief-counsel">U.S. Tax Court Requirements for Office of Chief Counsel Student Practice Program</a></strong>”).',
                    },
                    {
                        "type": "h2",
                        "value": "Procedures for Programs Currently Participating",
                    },
                    {
                        "type": "paragraph",
                        "value": 'In order for an academic clinic, nonacademic clinic or Bar sponsored calendar call program to participate, the clinic or Bar sponsored calendar call program director/coordinator must send a letter to the Chief Judge containing the information specified in section <strong><a href="/clinics-academic#SEC1">1(e)</a></strong> of the Requirements for Academic Clinics (Law School), section <strong><a href="/clinics-academic-non-law-school#SEC1">1(e)</a></strong> of the Requirements for Academic Clinics (Non Law School), section <strong><a href="/clinics-nonacademic#SEC1">1(g)</a></strong> of the Requirements for Nonacademic Clinics, and section <strong><a href="/clinics-calendar-call#SEC1">1(c)</a></strong> of the Requirements for Bar Sponsored Calendar call Programs by February 15 of each year. The Requirements include a sample of the letter the clinics and programs are requested to send to the Court. The Court will send a reminder of this requirement in January of each year to clinics and Bar sponsored calendar call programs already participating and will acknowledge receipt of the clinics’ and Bar sponsored calendar call programs’ letter requesting participation.',
                    },
                    {
                        "type": "h2",
                        "value": "Procedures for Programs Not Currently Participating",
                    },
                    {
                        "type": "paragraph",
                        "value": 'The Court invites academic and nonacademic tax clinics and Bar sponsored calendar call programs which do not currently participate to review the Court’s Requirements for participation and to consider submitting a request to participate in the Court’s program at anytime. Those clinics and programs should send a letter containing the information specified in section <strong><a href="/clinics-academic#SEC1">1(e)</a></strong> of the Requirements for Academic Clinics, section <strong><a href="/clinics-academic-non-law-school#SEC1">1(e)</a></strong> of the Requirements for Academic Clinics (Non Law School), section <strong><a href="/clinics-nonacademic#SEC1">1(g)</a></strong> of the Requirements for Nonacademic Clinics, and section <strong><a href="/clinics-calendar-call#SEC1">1(c)</a></strong> of the Requirements for Bar Sponsored Calendar Call Programs, except that academic clinics, academic clinics (non law school), nonacademic clinics, and Bar sponsored calendar call programs which are not currently participating need not provide the information requested in section <strong><a href="/clinics-academic#SEC1">1(e)(6)</a></strong>,<strong><a href="/clinics-academic-non-law-school#SEC1">1(e)(6)</a></strong>, <strong><a href="/clinics-nonacademic#SEC1">1(g)(5)</a></strong>, and <strong><a href="/clinics-calendar-call#SEC1">1(c)(6)</a></strong> of those Requirements, respectively. The Court will acknowledge receipt of the information.',
                    },
                    {
                        "type": "snippet",
                        "value": CommonText.objects.get(
                            name="Clinics Contact Details"
                        ).id,
                    },
                ],
            )
        )

        logger.info(f"Successfully created the '{title}' page.")
