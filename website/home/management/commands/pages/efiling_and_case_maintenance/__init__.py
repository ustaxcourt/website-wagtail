from .case_related_forms_page import CaseRelatedFormPageInitializer
from .dawson_page import DawsonPageInitializer
from .dawson_search_page import DawsonSearchPageInitializer
from .dawson_faqs_basics_page import DawsonFaqsBasicsPageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
    DawsonFaqsBasicsPageInitializer,
]
