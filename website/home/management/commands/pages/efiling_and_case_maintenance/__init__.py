from .case_related_forms_page import CaseRelatedFormPageInitializer
from .dawson_page import DawsonPageInitializer
from .dawson_search_page import DawsonSearchPageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    CaseRelatedFormPageInitializer,
    DawsonPageInitializer,
    DawsonSearchPageInitializer,
]
