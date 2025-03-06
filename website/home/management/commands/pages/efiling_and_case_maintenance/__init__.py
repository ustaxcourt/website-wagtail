from .case_related_forms_page import CaseRelatedFormPageInitializer
from .dawson_page import DawsonPageInitializer
from .dawson_search_page import DawsonSearchPageInitializer
from .dawson_faqs_basics_page import DawsonFaqsBasicsPageInitializer
from .dawson_faqs_case_management_page import DawsonFaqsCaseManagementPageInitializer
from .fill_in_form_instructions_page import FillInFormsInstructionsPageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
    DawsonFaqsBasicsPageInitializer,
    DawsonFaqsCaseManagementPageInitializer,
    FillInFormsInstructionsPageInitializer,
]
