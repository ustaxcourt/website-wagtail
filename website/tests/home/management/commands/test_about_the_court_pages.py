from tests.home.management.commands.base_page_initializer_test import (
    BasePageInitializerTestCase,
)
from wagtail.models import Page
from unittest.mock import MagicMock, patch

from home.management.commands.pages.about_the_court import (
    about_the_court_pages_to_initialize,
)

from home.management.commands.pages.about_the_court.employment_page import (
    EmploymentPageInitializer,
)
from home.management.commands.pages.about_the_court.judges_page import (
    JudgesPageInitializer,
)
from home.management.commands.pages.about_the_court.mission_page import (
    MissionPageInitializer,
)
from home.management.commands.pages.about_the_court.history_page import (
    HistoryPageInitializer,
)
from home.management.commands.pages.about_the_court.holidays_page import (
    HolidaysPageInitializer,
)
from home.management.commands.pages.about_the_court.vacancy_announcements_page import (
    VacancyAnnouncementsPageInitializer,
)
from home.management.commands.pages.about_the_court.law_clerk_program_page import (
    LawClerkProgramPageInitializer,
)
from home.management.commands.pages.about_the_court.reports_and_statistics_page import (
    ReportsAndStatisticsPageInitializer,
)
from home.management.commands.pages.about_the_court.directory_page import (
    DirectoryPageInitializer,
)
from home.management.commands.pages.about_the_court.judges_recruiting_page import (
    JudgesRecruitingPageInitializer,
)
from home.management.commands.pages.about_the_court.fees_and_charges_page import (
    FeesAndChargesPageInitializer,
)
from home.management.commands.pages.about_the_court.press_releases_page import (
    PressReleasesPageInitializer,
)
from home.management.commands.pages.about_the_court.internship_programs_page import (
    InternshipProgramsPageInitializer,
)

ABOUT_THE_COURT_PAGES = [
    (MissionPageInitializer, "mission"),
    (HistoryPageInitializer, "history"),
    (ReportsAndStatisticsPageInitializer, "reports-and-statistics"),
    (JudgesPageInitializer, "judges"),
    (EmploymentPageInitializer, "employment"),
    (HolidaysPageInitializer, "holidays"),
    # (VacancyAnnouncementsPageInitializer, "vacancy-announcements"),
    # (LawClerkProgramPageInitializer, "law-clerk-program"),
    (DirectoryPageInitializer, "directory"),
    # (JudgesRecruitingPageInitializer, "judges-recruiting"),
    (FeesAndChargesPageInitializer, "fees-and-charges"),
    (PressReleasesPageInitializer, "news-and-announcements"),
    # (InternshipProgramsPageInitializer, "internship-programs"),
]

ABOUT_THE_COURT_EMPLOYMENT_SUB_PAGES = [
    (VacancyAnnouncementsPageInitializer, "vacancy-announcements"),
    (LawClerkProgramPageInitializer, "law-clerk-program"),
    (JudgesRecruitingPageInitializer, "judges-recruiting"),
    (InternshipProgramsPageInitializer, "internship-programs"),
]


class TestAboutTheCourtPages(BasePageInitializerTestCase):
    def setUp(self):
        super().setUp()

    def test_count_of_pages_to_test_matches_expected(self):
        self.assertEqual(
            len(ABOUT_THE_COURT_PAGES) + len(ABOUT_THE_COURT_EMPLOYMENT_SUB_PAGES),
            len(about_the_court_pages_to_initialize),
        )

    def test_create_creates_page(self):
        # mock_commontext = MagicMock(id=1)
        for initializer, slug in ABOUT_THE_COURT_PAGES:
            with (
                self.subTest(initializer=initializer.__name__),
                # patch("home.models.CommonText.objects.get", return_value=mock_commontext)
            ):
                self.assertFalse(Page.objects.filter(slug=slug).exists())
                initializer().create()
                self.assertTrue(Page.objects.filter(slug=slug).exists())

    def test_create_creates_employment_sub_page(self):
        mock_judgeprofile = MagicMock(id=1)
        employmentPageInitializer = EmploymentPageInitializer()
        employmentPageInitializer.create()
        for initializer, slug in ABOUT_THE_COURT_EMPLOYMENT_SUB_PAGES:
            with (
                self.subTest(initializer=initializer.__name__),
                patch(
                    "home.models.JudgeProfile.objects.get",
                    return_value=mock_judgeprofile,
                ),
            ):
                self.assertFalse(Page.objects.filter(slug=slug).exists())
                initializer().create()
                self.assertTrue(Page.objects.filter(slug=slug).exists())

    def test_create_page_that_already_exists_writes_to_log_and_ends(self):
        mock_judgeprofile = MagicMock(id=1)
        for initializer, slug in (
            ABOUT_THE_COURT_PAGES + ABOUT_THE_COURT_EMPLOYMENT_SUB_PAGES
        ):
            mock_page = MagicMock(slug=slug)
            with (
                self.subTest(initializer=initializer.__name__),
                patch(
                    "home.models.JudgeProfile.objects.get",
                    return_value=mock_judgeprofile,
                ),
                patch("wagtail.models.Page.objects", return_value=[mock_page]),
                patch("logging.getLogger") as mock_logger,
            ):
                self.assertTrue(Page.objects.filter(slug=slug).exists())
                initializer().create()
                mock_logger.assert_called_once
