from wagtail.models import Page
import logging


from home.models.judges import (
    JudgeCollection,  # noqa: F401
    JudgeProfile,  # noqa: F401
    JudgeRole,  # noqa: F401
)
from home.models.settings import (
    Footer,  # noqa: F401
    GoogleAnalyticsSettings,  # noqa: F401
)
from home.models.config import IconCategories  # noqa: F401
from home.models.snippets.navigation import (
    NavigationRibbon,  # noqa: F401
    NavigationRibbonLink,  # noqa: F401
    NavigationMenu,  # noqa: F401
    SubNavigationLinkBlock,  # noqa: F401
)
from home.models.snippets.common import CommonText  # noqa: F401
from home.models.pages.standard import StandardPage
from home.models.custom_blocks.photo_dedication import PhotoDedicationBlock  # noqa: F401
from home.models.custom_blocks.common import CommonBlock, link_obj, ColumnBlock  # noqa: F401
from home.models.custom_blocks.alert_message import AlertMessageBlock  # noqa: F401
from home.models.custom_blocks.button import ButtonBlock  # noqa: F401
from home.models.pages.enhanced_standard import EnhancedStandardPage  # noqa: F401
from home.models.pages.enhanced_standard import IndentStyle  # noqa: F401
from home.models.pages.trial import PlacesOfTrialPage  # noqa: F401
from home.models.pages.pamphlet import PamphletsPage, PamphletEntry  # noqa: F401
from home.models.pages.release_notes import ReleaseNotes  # noqa: F401
from home.models.pages.internship import InternshipPrograms  # noqa: F401
from home.models.pages.press_release import PressReleasePage  # noqa: F401
from home.models.pages.home_page import HomePage, HomePageEntry, HomePageImage  # noqa: F401
from home.models.pages.administrative_orders import (
    AdministrativeOrdersPage,  # noqa: F401
    PDFs,  # noqa: F401
)
from home.models.pages.case_related_forms import (
    CaseRelatedFormsEntry,  # noqa: F401
    CaseRelatedFormsPage,  # noqa: F401
)
from home.models.pages.directory import DirectoryIndex  # noqa: F401
from home.models.pages.judge_index import JudgeIndex, JudgeColumnBlock, JudgeColumns  # noqa: F401
from home.models.pages.csv_upload import CSVUploadPage  # noqa: F401
from home.models.pages.vacancy_announcements import (
    VacancyAnnouncementsPage,  # noqa: F401
    VacancyEntry,  # noqa: F401
)
from home.models.pages.judges_recruiting import JudgesRecruiting  # noqa: F401
from home.models.pages.enhanced_raw_html import EnhancedRawHTMLPage  # noqa: F401
from home.models.pages.dawson import (
    SimpleCard,  # noqa: F401
    RelatedPage,  # noqa: F401
    SimpleCardGroup,  # noqa: F401
    FancyCard,  # noqa: F401
    PhotoDedication,  # noqa: F401
    DawsonPage,  # noqa: F401
)


logger = logging.getLogger(__name__)


class ExternalRedirectPage(Page):
    class Meta:
        abstract = False


class RedirectPage(StandardPage):
    content_panels = StandardPage.content_panels
