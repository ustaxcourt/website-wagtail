from .case_related_forms_page import CaseRelatedFormPageInitializer
from .dawson_page import DawsonPageInitializer
from .dawson_search_page import DawsonSearchPageInitializer
from .dawson_faqs_basics_page import DawsonFaqsBasicsPageInitializer
from .dawson_faqs_account_management_page import (
    DawsonFaqsAccountManagementPageInitializer,
)
from .fill_in_form_instructions_page import FillInFormsInstructionsPageInitializer
from .searches_and_public_access_page import SearchesAndPublicAccessPageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    DawsonFaqsBasicsPageInitializer,
    DawsonFaqsAccountManagementPageInitializer,
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
    FillInFormsInstructionsPageInitializer,
    SearchesAndPublicAccessPageInitializer,
]
