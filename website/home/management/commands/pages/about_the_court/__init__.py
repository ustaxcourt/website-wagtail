from .employment_page import EmploymentPageInitializer
from .judges_page import JudgesPageInitializer
from .mission_page import MissionPageInitializer
from .history_page import HistoryPageInitializer
from .holidays_page import HolidaysPageInitializer
from .vacancy_announcements_page import VacancyAnnouncementsPageInitializer
from .law_clerk_program_page import LawClerkProgramPageInitializer
from .trial_sessions_page import TrialSessionsPageInitializer
from .reports_and_statistics_page import ReportsAndStatisticsPageInitializer
from .directory_page import DirectoryPageInitializer
from .judges_recruiting_page import JudgesRecruitingPageInitializer
from .fees_and_charges_page import FeesAndChargesPageInitializer
from .press_releases_page import PressReleasesPageInitializer
from .internship_programs_page import InternshipProgramsPageInitializer

about_the_court_pages_to_initialize = [
    #  Order matters for menu
    MissionPageInitializer,
    HistoryPageInitializer,
    ReportsAndStatisticsPageInitializer,
    JudgesPageInitializer,
    TrialSessionsPageInitializer,
    EmploymentPageInitializer,
    HolidaysPageInitializer,
    VacancyAnnouncementsPageInitializer,  # this must come after employment page
    LawClerkProgramPageInitializer,
    DirectoryPageInitializer,
    JudgesRecruitingPageInitializer,
    FeesAndChargesPageInitializer,
    PressReleasesPageInitializer,
    InternshipProgramsPageInitializer,
]
