from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import DirectoryIndex, JudgeCollection
import logging

logger = logging.getLogger(__name__)


class DirectoryPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "directory"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Directory"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return
        logger.info(f"Creating the '{title}' page.")

        new_page = home_page.add_child(
            instance=DirectoryIndex(
                title=title,
                slug="directory",
                seo_title=title,
                search_description=title,
                body=[
                    {
                        "type": "directory",
                        "value": [
                            {"type": "h2", "value": "Office of the Clerk of the Court"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "The Clerk's Office is responsible for, among other things, the business management and operations of the Court. General procedure questions can be directed here.",
                                        "phone_number": "(202) 521-0700",
                                    },
                                ],
                            },
                            {"type": "hr", "value": True},
                            {
                                "type": "h2",
                                "value": "Request for Tax Court Rules of Practice and Procedure",
                            },
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "Tax Court Rules of Practice and Procedure are also available <a href='/rules' title='Rules'>online</a>.",
                                        "phone_number": "(202) 521-0700",
                                    },
                                ],
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Admissions"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "Admissions procedures for practice before the Tax Court and practitioner access for DAWSON.",
                                        "phone_number": "(202) 521-4629",
                                    },
                                ],
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Case Processing"},
                            {"type": "h3", "value": "Petitions Filing"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "Petition for Small Tax Cases is available on the <a href='/case-related-forms' title='Case Related Forms'>Forms</a> page.",
                                        "phone_number": "(202) 521-0700",
                                    },
                                ],
                            },
                            {"type": "h3", "value": "Copies and Records Requests"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "See <a href='/transcripts-and-copies' title='Transcripts and Copies'>Transcripts and Copies</a>.",
                                        "phone_number": "(202) 521-4688",
                                    },
                                ],
                            },
                            {"type": "h3", "value": "Docket Information"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": """(1) Documents and pleadings filed subsequent to petitions;<br/>
(2) Action taken on documents filed;<br/>
(3) Status of cases.""",
                                        "phone_number": "(202) 521-4650",
                                    },
                                ],
                            },
                            {"type": "h3", "value": "Appeals Information"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": """(1) Filing of notices of appeal from Tax Court decisions;<br/>
(2) Other procedures relating to appellate review of Tax Court decisions.""",
                                        "phone_number": "(202) 521-4650",
                                    },
                                ],
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Human Resources"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "Also see the <a href='/employment' title='Employment'>Employment</a> page.",
                                        "phone_number": "(202) 521-4700",
                                    },
                                ],
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Public Affairs"},
                            {
                                "type": "DirectoryEntry",
                                "value": [
                                    {
                                        "description": "Media inquiries and general questions.",
                                        "phone_number": "(202) 521-3355",
                                    },
                                ],
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Judge Chambers"},
                            {
                                "type": "JudgeCollection",
                                "value": JudgeCollection.objects.filter(name="Judges")
                                .first()
                                .id,
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Senior Judge Chambers"},
                            {
                                "type": "JudgeCollection",
                                "value": JudgeCollection.objects.filter(
                                    name="Senior Judges"
                                )
                                .first()
                                .id,
                            },
                            {"type": "hr", "value": True},
                            {"type": "h2", "value": "Special Trial Judge Chambers"},
                            {
                                "type": "JudgeCollection",
                                "value": JudgeCollection.objects.filter(
                                    name="Special Trial Judges"
                                )
                                .first()
                                .id,
                            },
                        ],
                    }
                ],
            )
        )

        new_page.save()
