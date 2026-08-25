from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon, IconCategories
from home.models import EnhancedStandardPage
from home.management.commands.snippets.navigation_ribbon import ribbon_snippet_name
import logging

logger = logging.getLogger(__name__)


class GuidenceForPetitionersPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners"
        title = "Guidance for Petitioners"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        document = self.load_document_from_documents_dir(
            subdirectory=None,
            filename="DAWSON_Petitioner_Training_Guide.pdf",
            title="DAWSON Self-Represented (Pro Se) Training Guide",
        )

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=ribbon_snippet_name
        ).first()

        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Guidance for Petitioners",
                body=[
                    {"type": "h2", "value": "Introduction"},
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "This guide provides information, but not legal advice, for individuals who represent themselves before the Tax Court. It answers some of taxpayers' most frequent questions. It is a brief step-by-step explanation of the process of:",
                    },
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "Starting A Case",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-start",
                                },
                                {
                                    "title": "Things that occur before trial",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-before",
                                },
                                {
                                    "title": "Things that occur during trial",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-during",
                                },
                                {
                                    "title": "Things that occur after trial",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-after",
                                },
                                {
                                    "title": "Guidance for Self-Represented Petitioners",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-guidance",
                                },
                                {
                                    "title": "Process and Timeline",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-timeline",
                                },
                                {
                                    "title": "Prepare to File",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-prepare-to-file",
                                },
                                {
                                    "title": "Forms to File a Petition",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-forms",
                                },
                                {
                                    "title": "Frequently Asked Questions",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/petitioners-help",
                                },
                            ],
                        },
                    },
                    {
                        "type": "paragraph",
                        "value": "A <strong>User Guide</strong> for the Court’s electronic filing and case management system, is also available.",
                    },
                    {"type": "h2", "value": "Additional Resources"},
                    {"type": "hr", "value": True},
                    {
                        "type": "links",
                        "value": {
                            "links": [
                                {
                                    "title": "DAWSON Self-Represented (Pro Se) Training Guide",
                                    "icon": IconCategories.PDF,
                                    "document": document.id,
                                    "url": None,
                                },
                                {
                                    "title": "Definitions",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/definitions",
                                },
                                {
                                    "title": " Clinic Program Information",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/clinics",
                                },
                                {
                                    "title": "Case Procedure Information",
                                    "icon": IconCategories.INFO,
                                    "document": None,
                                    "url": "/case-procedure",
                                },
                            ]
                        },
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "For more detailed information, consult the Tax Court <a href='/rules'>Rules of Practice and Procedure</a>.",
                    },
                ],
            )
        )
