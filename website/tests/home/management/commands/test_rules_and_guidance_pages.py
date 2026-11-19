from tests.home.management.commands.base_page_initializer_test import (
    BasePageInitializerTestCase,
)
from wagtail.models import Page
from unittest.mock import MagicMock, patch

from home.management.commands.pages.rules_and_guidance import (
    rules_and_guidance_pages_to_initialize,
)

from home.management.commands.pages.rules_and_guidance.case_procedure_page import (
    CaseProcedurePageInitializer,
)
from home.management.commands.pages.rules_and_guidance.administrative_orders_page import (
    AdministrativeOrdersPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.clinics_pro_bono_page import (
    ClinicsProBonoProgramsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.getting_ready_page import (
    GettingReadyPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.guidence_for_petitioners import (
    GuidenceForPetitionersPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.guidence_for_practitioners_page import (
    GuidenceForPractitionersPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_about_page import (
    PetitionersAboutInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_after_trial_page import (
    PetitionersAfterTrialInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_before_trial_page import (
    PetitionersBeforeTrialInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_during_page import (
    PetitionersDuringPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_start_page import (
    PetitionersStartPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.remote_basics import (
    RemoteBasicsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.remote_proceedings_page import (
    RemoteProceedingsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.remote_proceedings_calendar_page import (
    RemoteProceedingsCalendarPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.zoomgov_proceedings_page import (
    ZoomgovProceedingPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.judicial_conduct_and_disability_procedures_page import (
    JudicialConductAndDisabilityProceduresPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.jcdp_orders_issued_page import (
    JCDPOrdersIssuedStartPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.notices_of_rule_amendments_page import (
    NoticesOfRuleAmendmentsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.rules_page import (
    RulesPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.clinics_academic_page import (
    ClinicsAcademicPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.clinics_academic_non_law_school_page import (
    ClinicsAcademicNonLawSchoolPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.clinics_nonacademic_page import (
    ClinicsNonAcademicPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.clinics_calendar_call_page import (
    ClinicsCalendarCallPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.clinics_chief_counsel_page import (
    ClinicsChiefCounselPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.comments_and_suggestions_page import (
    CommentsAndSuggestionsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_guidance import (
    PetitionersGuidancePageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_timeline import (
    PetitionersTimelinePageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_prepare_to_file import (
    PetitionersPrepareToFilePageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_forms import (
    PetitionersFormsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_help import (
    PetitionersHelpPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.petitioners_help_rules_link import (
    PetitionersHelpRulesLinkUpdater as PetitionersHelpRulesLinkUpdater,
)

RULES_AND_GUIDANCE_PAGES = [
    (RemoteProceedingsPageInitializer, "zoomgov"),
    (RemoteProceedingsCalendarPageInitializer, "remote-proceedings"),
    (AdministrativeOrdersPageInitializer, "administrative-orders"),
    (RulesPageInitializer, "rules"),
    (GuidenceForPetitionersPageInitializer, "petitioners"),
    (ClinicsProBonoProgramsPageInitializer, "clinics"),
    (GuidenceForPractitionersPageInitializer, "practitioners"),
    # NON-TOP LEVEL PAGES. Order does not matter.
    (PetitionersStartPageInitializer, "petitioners-start"),
    (PetitionersAboutInitializer, "petitioners-about"),
    (PetitionersDuringPageInitializer, "petitioners-during"),
    (PetitionersBeforeTrialInitializer, "petitioners-before"),
    (PetitionersAfterTrialInitializer, "petitioners-after"),
    (RemoteBasicsPageInitializer, "zoomgov-the-basics"),
    (ZoomgovProceedingPageInitializer, "zoomgov-zoomgov-proceedings"),
    (GettingReadyPageInitializer, "zoomgov-getting-ready"),
    (JudicialConductAndDisabilityProceduresPageInitializer, "jcdp"),
    (ClinicsAcademicPageInitializer, "clinics-academic"),
    (ClinicsAcademicNonLawSchoolPageInitializer, "clinics-academic-non-law-school"),
    (ClinicsNonAcademicPageInitializer, "clinics-nonacademic"),
    (ClinicsCalendarCallPageInitializer, "clinics-calendar-call"),
    (ClinicsChiefCounselPageInitializer, "clinics-chief-counsel"),
    (NoticesOfRuleAmendmentsPageInitializer, "notices-of-rule-amendments"),
    (CaseProcedurePageInitializer, "case-procedure"),
    (JCDPOrdersIssuedStartPageInitializer, "jcdp-orders-issued"),
    (CommentsAndSuggestionsPageInitializer, "rules-comments"),
    (PetitionersGuidancePageInitializer, "petitioners-guidance"),
    (PetitionersTimelinePageInitializer, "petitioners-timeline"),
    (PetitionersPrepareToFilePageInitializer, "petitioners-prepare-to-file"),
    (PetitionersFormsPageInitializer, "petitioners-forms"),
    (PetitionersHelpPageInitializer, "petitioners-help"),
]


class TestRulesAndGuidancePages(BasePageInitializerTestCase):
    def setUp(self):
        super().setUp()

    def test_count_of_pages_to_test_matches_expected(self):
        self.assertEqual(
            len(RULES_AND_GUIDANCE_PAGES), len(rules_and_guidance_pages_to_initialize)
        )

    def test_create_creates_page(self):
        mock_commontext = MagicMock(id=1)
        for initializer, slug in RULES_AND_GUIDANCE_PAGES:
            with (
                self.subTest(initializer=initializer.__name__),
                patch(
                    "home.models.CommonText.objects.get", return_value=mock_commontext
                ),
            ):
                self.assertFalse(Page.objects.filter(slug=slug).exists())
                initializer().create()
                self.assertTrue(Page.objects.filter(slug=slug).exists())

    def test_create_page_that_already_exists_writes_to_log_and_ends(self):
        mock_commontext = MagicMock(id=1)
        for initializer, slug in [
            x for x in RULES_AND_GUIDANCE_PAGES if x[1] != "petitioners-guidance"
        ]:
            mock_page = MagicMock(slug=slug)
            with (
                self.subTest(initializer=initializer.__name__),
                patch(
                    "home.models.CommonText.objects.get", return_value=mock_commontext
                ),
                patch("wagtail.models.Page.objects", return_value=[mock_page]),
                patch("logging.getLogger") as mock_logger,
            ):
                self.assertTrue(Page.objects.filter(slug=slug).exists())
                initializer().create()
                mock_logger.assert_called_once
