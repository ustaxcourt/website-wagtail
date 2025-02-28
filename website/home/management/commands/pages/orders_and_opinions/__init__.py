from .citation_style_manual_page import CitationStyleManualPageInitializer
from .pamphlets_page import PamphletsPageInitializer
from .search_page import SearchPageInitializer
from .todays_opinions import TodaysOpinionsPageInitializer
from .todays_orders import TodaysOrdersPageInitializer
from .transcripts_and_copies_page import TranscriptsAndCopiesPageInitializer


orders_and_opinions_pages_to_initialize = [
    TodaysOrdersPageInitializer,
    TodaysOpinionsPageInitializer,
    SearchPageInitializer,
    CitationStyleManualPageInitializer,
    TranscriptsAndCopiesPageInitializer,
    PamphletsPageInitializer,
]
