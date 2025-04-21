from .case_related_forms_page import CaseRelatedFormPageInitializer
from .dawson_page import DawsonPageInitializer
from .dawson_account_practitioner import DawsonAccountPractitionerPageInitializer
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
from .dawson_pay_filing_fee import DawsonPayFilingFeeInitializer
from .merging_files_page import MergingFilesPageInitializer
from .notice_regarding_privacy_page import NoticeRegardingPrivacyPageInitializer
from .efile_a_petition_page import EfileAPetitionPageInitializer
from .update_contact_information_page import UpdateContactInformationPageInitializer
from .dawson_release_notes import DawsonReleaseNotesInitializer
from .dawson_terms_of_use import DawsonTermsOfUsePageInitializer


efiling_and_case_maintenance_pages_to_initialize = [
    # DAWSON page depends on the other DAWSON pages
    DocumentsEligibleEfilingPageInitializer,
    MergingFilesPageInitializer,
    DawsonTermsOfUsePageInitializer,
    EfileAPetitionPageInitializer,
    UpdateContactInformationPageInitializer,
    DawsonAccountPractitionerPageInitializer,
    DawsonUserGuidesPageInitializer,
    DawsonFaqsBasicsPageInitializer,
    DawsonFaqsAccountManagementPageInitializer,
    DawsonFaqsTrainingAndSupportPageInitializer,
    DawsonFaqsCaseManagementPageInitializer,
    DawsonFaqsDefinitionsPageInitializer,
    NoticeRegardingPrivacyPageInitializer,
    DawsonFindAnOrderPageInitializer,
    DawsonFindAnOpinionPageInitializer,
    DawsonReleaseNotesInitializer,
    FindACasePageInitializer,
    DawsonPayFilingFeeInitializer,
    # Order of initialization matters
    DashboardPageInitializer,
    DawsonPageInitializer,
    CaseRelatedFormPageInitializer,
    # Other pages, order does not matter
    FillInFormsInstructionsPageInitializer,
    SearchesAndPublicAccessPageInitializer,
]
