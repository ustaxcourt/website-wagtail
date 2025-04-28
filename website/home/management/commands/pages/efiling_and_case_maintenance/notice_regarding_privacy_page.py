from wagtail.models import Page
from home.models import EnhancedStandardPage
from home.management.commands.pages.page_initializer import PageInitializer
import logging

logger = logging.getLogger(__name__)


class NoticeRegardingPrivacyPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "notice-regarding-privacy"

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Notice Regarding Privacy and Public Access to Case Files"
        slug = self.slug

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": "Pursuant to 26 USC Section 7461(a), all reports of the Tax Court and all evidence received by the Tax Court, including a transcript of the record of the hearings, generally are public records open to inspection by the public. In order to provide access to case files while also protecting personal privacy and other legitimate interests, parties are encouraged to refrain from including or to take appropriate steps to redact the following information from all pleadings and papers filed with the Court, in electronic or paper form, including exhibits thereto, except as otherwise required by the Court’s Rules or as directed by the Court:",
                    },
                    {
                        "type": "list",
                        "value": {
                            "list_type": "ordered",
                            "items": [
                                {
                                    "text": "Taxpayer identification numbers (e.g., Social Security numbers or Employer Identification numbers);",
                                },
                                {
                                    "text": "Dates of birth. If a date of birth is provided, only the year should appear;",
                                },
                                {
                                    "text": "Names of minor children. If a minor child is identified, only the minor child’s initials should appear; and",
                                },
                                {
                                    "text": "Financial account numbers. If a financial account number is provided, only the last four digits of the number should appear.",
                                },
                            ],
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": "Pursuant to 26 USC Section 7461(b), and Rules 27 and 103, Tax Court Rules of Practice and Procedure, a party wishing to file a document containing personal identifiers listed above may file a motion to seal and submit with the motion the unredacted document. If the document is sealed, the Court may still require the party to file a redacted document for the public record.",
                    },
                    {
                        "type": "paragraph",
                        "value": "A person waives protection as to the person’s own information by filing it without redaction and not under seal. The Clerk of the Court is not required to review documents filed with the Court for compliance with this Notice. The responsibility to redact filings rests with the party or nonparty making the filing. The Court expects the parties to exercise good faith in their efforts to redact.",
                    },
                ],
                search_description="Notice regarding privacy and public access to case file",
            )
        )

        new_page.save_revision().publish()
        logger.info(f"Successfully created the '{title}' page.")
