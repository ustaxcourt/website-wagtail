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
from .definitions_page import DawsonFaqsDefinitionsPageInitializer
from .find_order_page import DawsonFindAnOrderPageInitializer
from .find_an_opinion import DawsonFindAnOpinionPageInitializer
from .dawson_find_a_case import FindACasePageInitializer
from .documents_eligible_for_efiling_page import DocumentsEligibleEfilingPageInitializer
from .merging_files_page import MergingFilesPageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    # DAWSON page depends on the other DAWSON pages
    DocumentsEligibleEfilingPageInitializer,
    # DAWSON page depends on the user guides page
    MergingFilesPageInitializer,
    DawsonUserGuidesPageInitializer,
    DawsonFaqsBasicsPageInitializer,
    DawsonFaqsAccountManagementPageInitializer,
    DawsonFaqsTrainingAndSupportPageInitializer,
    DawsonFaqsCaseManagementPageInitializer,
    DawsonFaqsDefinitionsPageInitializer,
    DawsonFindAnOrderPageInitializer,
    DawsonFindAnOpinionPageInitializer,
    FindACasePageInitializer,
    # Order of initialization matters
    DashboardPageInitializer,
    DawsonSearchPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
    # Other pages, order does not matter
    FillInFormsInstructionsPageInitializer,
    SearchesAndPublicAccessPageInitializer,
]
