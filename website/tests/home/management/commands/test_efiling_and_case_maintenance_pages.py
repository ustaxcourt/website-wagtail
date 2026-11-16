from tests.home.management.commands.base_page_initializer_test import (
    BasePageInitializerTestCase,
)
from wagtail.models import Page
from unittest.mock import MagicMock, patch

from home.management.commands.pages.efiling_and_case_maintenance import (
    efiling_and_case_maintenance_pages_to_initialize,
)

from home.management.commands.pages.efiling_and_case_maintenance.case_related_forms_page import (
    CaseRelatedFormPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_page import (
    DawsonPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_account_practitioner import (
    DawsonAccountPractitionerPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_faqs_basics_page import (
    DawsonFaqsBasicsPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_faqs_account_management_page import (
    DawsonFaqsAccountManagementPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.fill_in_form_instructions_page import (
    FillInFormsInstructionsPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_faqs_training_and_support import (
    DawsonFaqsTrainingAndSupportPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.definitions_page import (
    DefinitionsPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.searches_and_public_access_page import (
    SearchesAndPublicAccessPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_faqs_case_management_page import (
    DawsonFaqsCaseManagementPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_user_guides_page import (
    DawsonUserGuidesPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dashboard_page import (
    DashboardPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.find_order_page import (
    DawsonFindAnOrderPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.find_an_opinion import (
    DawsonFindAnOpinionPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_find_a_case import (
    FindACasePageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.documents_eligible_for_efiling_page import (
    DocumentsEligibleEfilingPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_pay_filing_fee import (
    DawsonPayFilingFeeInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.merging_files_page import (
    MergingFilesPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.notice_regarding_privacy_page import (
    NoticeRegardingPrivacyPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.efile_a_petition_page import (
    EfileAPetitionPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.update_contact_information_page import (
    UpdateContactInformationPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_release_notes import (
    DawsonReleaseNotesInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.dawson_terms_of_use import (
    DawsonTermsOfUsePageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.places_of_trial_page import (
    PlacesOfTrialPageInitializer,
)
from home.management.commands.pages.efiling_and_case_maintenance.LITC_page import (
    LITCPageInitializer,
)

EFILING_AND_CASE_MAINTENANCE_PAGES = [
    (DocumentsEligibleEfilingPageInitializer, "documents-eligible-for-efiling"),
    (MergingFilesPageInitializer, "merging-files"),
    (DawsonTermsOfUsePageInitializer, "dawson-tou"),
    (EfileAPetitionPageInitializer, "efile-a-petition"),
    (UpdateContactInformationPageInitializer, "update-contact-information"),
    (DawsonAccountPractitionerPageInitializer, "dawson-account-practitioner"),
    (DawsonUserGuidesPageInitializer, "dawson-user-guides"),
    (DawsonFaqsBasicsPageInitializer, "dawson-faqs-basics"),
    (DawsonFaqsAccountManagementPageInitializer, "dawson-faqs-account-management"),
    (DawsonFaqsTrainingAndSupportPageInitializer, "dawson-faqs-training-and-support"),
    (DawsonFaqsCaseManagementPageInitializer, "dawson-faqs-case-management"),
    (NoticeRegardingPrivacyPageInitializer, "notice-regarding-privacy"),
    (DefinitionsPageInitializer, "definitions"),
    (DawsonFindAnOrderPageInitializer, "find-an-order"),
    (DawsonFindAnOpinionPageInitializer, "find-an-opinion"),
    (DawsonReleaseNotesInitializer, "release-notes"),
    (FindACasePageInitializer, "find-a-case"),
    (DawsonPayFilingFeeInitializer, "pay-filing-fee"),
    # Order of initialization matters
    (DashboardPageInitializer, "dashboard"),
    (DawsonPageInitializer, "dawson"),
    (CaseRelatedFormPageInitializer, "case-related-forms"),
    # Other pages, order does not matter
    (PlacesOfTrialPageInitializer, "dpt-cities"),
    (FillInFormsInstructionsPageInitializer, "forms-instructions"),
    (SearchesAndPublicAccessPageInitializer, "dawson-faqs-searches-public-access"),
    (LITCPageInitializer, "clinics-and-pro-bono-programs"),
]


class TestEfilingAndCaseManagementPages(BasePageInitializerTestCase):
    def setUp(self):
        super().setUp()

    def test_count_of_pages_to_test_matches_expected(self):
        self.assertEqual(
            len(EFILING_AND_CASE_MAINTENANCE_PAGES),
            len(efiling_and_case_maintenance_pages_to_initialize),
        )

    def test_create_creates_page(self):
        for initializer, slug in EFILING_AND_CASE_MAINTENANCE_PAGES:
            with (
                self.subTest(initializer=initializer.__name__),
            ):
                self.assertFalse(Page.objects.filter(slug=slug).exists())
                initializer().create()
                self.assertTrue(Page.objects.filter(slug=slug).exists())

    def test_create_page_that_already_exists_writes_to_log_and_ends(self):
        mock_caserelatedform = MagicMock(formName="abc.pdf")
        for initializer, slug in EFILING_AND_CASE_MAINTENANCE_PAGES:
            mock_page = MagicMock(slug=slug)
            with (
                self.subTest(initializer=initializer.__name__),
                patch(
                    "home.models.CaseRelatedFormsEntry.objects.filter",
                    return_value=mock_caserelatedform,
                ),
                patch("wagtail.models.Page.objects", return_value=[mock_page]),
                patch("logging.getLogger") as mock_logger,
            ):
                self.assertTrue(Page.objects.filter(slug=slug).exists())
                initializer().create()
                mock_logger.assert_called_once
