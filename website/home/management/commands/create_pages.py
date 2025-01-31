from django.core.management.base import BaseCommand
from home.management.commands.pages.case_related_forms_page import (
    CaseRelatedFormPageInitializer,
)
from home.management.commands.pages.dawson_page import DawsonPageInitializer
from home.management.commands.pages.dawson_search_page import (
    DawsonSearchPageInitializer,
)
from home.management.commands.pages.home_page import HomePageInitializer
from home.management.commands.pages.footer import FooterInitializer
from home.management.commands.pages.transcripts_and_copies_page import (
    TranscriptsAndCopiesPageInitializer,
)
from home.management.commands.pages.citation_style_manual_page import (
    CitationStyleManualPageInitializer,
)
from home.management.commands.pages.search_page import SearchPageInitializer
from home.management.commands.pages.todays_orders import TodaysOrdersPageInitializer
from home.management.commands.pages.todays_opinions import TodaysOpinionsPageInitializer
from home.management.commands.pages.remote_proceedings_page import (
    RemoteProceedingsPageInitializer,
)
from home.management.commands.pages.pamphlets_page import PamphletsPageInitializer

other_pages_to_initialize = [
    HomePageInitializer,
    FooterInitializer,
]

# NOTE, the order of these dictates the order in the dropdowns.
orders_opinions_pages_to_initialize = [
    TodaysOrdersPageInitializer,
    TodaysOpinionsPageInitializer,
    SearchPageInitializer,
    CitationStyleManualPageInitializer,
    TranscriptsAndCopiesPageInitializer,
    PamphletsPageInitializer,
]

# NOTE, the order of these dictates the order in the dropdowns.
efiling_pages_to_initialize = [
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
]

rules_and_guidance = [
    RemoteProceedingsPageInitializer,
]

pages_to_initialize = (
    other_pages_to_initialize
    + rules_and_guidance
    + efiling_pages_to_initialize
    + orders_opinions_pages_to_initialize
)


class Command(BaseCommand):
    help = "Create initial pages and form records if they don't already exist."

    def handle(self, *args, **options):
        for page_class in pages_to_initialize:
            page_instance = page_class(self.stdout)
            page_instance.create()

        self.stdout.write(self.style.SUCCESS("All pages have been initialized."))
