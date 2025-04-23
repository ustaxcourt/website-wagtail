from .citation_style_manual_page import CitationStyleManualPageInitializer
from .pamphlets_page import PamphletsPageInitializer
from .transcripts_and_copies_page import TranscriptsAndCopiesPageInitializer


orders_and_opinions_pages_to_initialize = [
    CitationStyleManualPageInitializer,
    TranscriptsAndCopiesPageInitializer,
    PamphletsPageInitializer,
]
