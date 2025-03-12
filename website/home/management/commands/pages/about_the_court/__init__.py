from .employment_page import EmploymentPageInitializer
from .judges_page import JudgesPageInitializer
from .mission_page import MissionPageInitializer
from .history_page import HistoryPageInitializer
from .holidays_page import HolidaysPageInitializer
from .vacancy_announcements_page import VacancyAnnouncementsPageInitializer


about_the_court_pages_to_initialize = [
    MissionPageInitializer,
    JudgesPageInitializer,
    EmploymentPageInitializer,
    HistoryPageInitializer,
    HolidaysPageInitializer,
    VacancyAnnouncementsPageInitializer,
]
