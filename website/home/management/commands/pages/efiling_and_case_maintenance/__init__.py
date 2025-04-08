from .case_related_forms_page import CaseRelatedFormPageInitializer
from .dawson_page import DawsonPageInitializer
from .dawson_search_page import DawsonSearchPageInitializer
from .dawson_faqs_basics_page import DawsonFaqsBasicsPageInitializer
from .dawson_faqs_account_management_page import (
    DawsonFaqsAccountManagementPageInitializer,
)
from .fill_in_form_instructions_page import FillInFormsInstructionsPageInitializer
from .dawson_faqs_training_and_support import (
    DawsonFaqsTrainingAndSupportPageInitializer,
)
from .searches_and_public_access_page import SearchesAndPublicAccessPageInitializer
from .dawson_faqs_case_management_page import DawsonFaqsCaseManagementPageInitializer
from .dawson_user_guides_page import DawsonUserGuidesPageInitializer
from .dashboard_page import DashboardPageInitializer
from .dawson_find_a_case import FindACasePageInitializer
from .documents_eligible_for_efiling_page import DocumentsEligibleEfilingPageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    DocumentsEligibleEfilingPageInitializer,
    # DAWSON page depends on the user guides page
    DawsonUserGuidesPageInitializer,
    FindACasePageInitializer,
    # Order of initialization matters
    DashboardPageInitializer,
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
    # Other pages, order does not matter
    FillInFormsInstructionsPageInitializer,
    SearchesAndPublicAccessPageInitializer,
    DawsonFaqsBasicsPageInitializer,
    DawsonFaqsAccountManagementPageInitializer,
    DawsonFaqsTrainingAndSupportPageInitializer,
    DawsonFaqsCaseManagementPageInitializer,
]
