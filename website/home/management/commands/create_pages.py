from django.core.management.base import BaseCommand
from home.management.commands.pages.case_related_forms_page import (
    CaseRelatedFormPageInitializer,
)
from home.management.commands.pages.dawson_page import DawsonPageInitializer
from home.management.commands.pages.dawson_search_page import (
    DawsonSearchPageInitializer,
)
from home.management.commands.pages.home_page import HomePageInitializer
from home.management.commands.pages.redirect_page import RedirectPageInitializer
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
from home.management.commands.pages.zoomgov_proceedings_page import (
    ZoomgovProceedingPageInitializer,
)
from home.management.commands.pages.pamphlets_page import PamphletsPageInitializer
from home.management.commands.pages.guidence_for_petitioners import (
    GuidenceForPetitionersPageInitializer,
)
from home.management.commands.snippets.navigation_ribbon import (
    NavigationRibbonInitializer,
)
from home.management.commands.pages.petitioners_start_page import (
    PetitionersStartPageInitializer,
)
from home.management.commands.pages.petitioners_before_trial_page import (
    PetitionersBeforeTrialInitializer,
)
from home.management.commands.pages.administrative_orders_page import (
    AdministrativeOrdersPageInitializer,
)
from home.management.commands.snippets.zoomgov_proceeding_ribbon import (
    ZoomgovProceedingRibbonInitializer,
)
from home.management.commands.pages.petitioners_glossary_page import (
    PetitionersGlossaryPageInitializer,
)
from home.management.commands.pages.remote_basics import RemoteBasicsPageInitializer

other_pages_to_initialize = [
    HomePageInitializer,
    FooterInitializer,
    RedirectPageInitializer,
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
    GuidenceForPetitionersPageInitializer,
    AdministrativeOrdersPageInitializer,
    PetitionersStartPageInitializer,
    PetitionersBeforeTrialInitializer,
    PetitionersGlossaryPageInitializer,
    RemoteBasicsPageInitializer,
    ZoomgovProceedingPageInitializer,
]

pages_to_initialize = (
    other_pages_to_initialize
    + rules_and_guidance
    + efiling_pages_to_initialize
    + orders_opinions_pages_to_initialize
)

snippets_to_initialize = [
    NavigationRibbonInitializer,
    ZoomgovProceedingRibbonInitializer,
]


class Command(BaseCommand):
    help = "Create initial pages and form records if they don't already exist."

    def handle(self, *args, **options):
        for snippet_class in snippets_to_initialize:
            snippet_instance = snippet_class(self.stdout)
            snippet_instance.create()

        for page_class in pages_to_initialize:
            page_instance = page_class(self.stdout)
            page_instance.create()

        self.stdout.write(self.style.SUCCESS("All pages have been initialized."))
