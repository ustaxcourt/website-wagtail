from .employment_page import EmploymentPageInitializer
from .judges_page import JudgesPageInitializer
from .mission_page import MissionPageInitializer
from .history_page import HistoryPageInitializer
from .holidays_page import HolidaysPageInitializer
from .vacancy_announcements_page import VacancyAnnouncementsPageInitializer
from .law_clerk_program_page import LawClerkProgramPageInitializer
from .trial_sessions_page import TrialSessionsPageInitializer


about_the_court_pages_to_initialize = [
    #  Order matters for menu
    MissionPageInitializer,
    HistoryPageInitializer,
    JudgesPageInitializer,
    TrialSessionsPageInitializer,
    EmploymentPageInitializer,
    HolidaysPageInitializer,
    VacancyAnnouncementsPageInitializer,  # this must come after employment page
    LawClerkProgramPageInitializer,
]
