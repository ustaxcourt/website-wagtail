from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
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


logger = logging.getLogger(__name__)


class ExternalRedirectPage(Page):
    class Meta:
        abstract = False


class RelatedPage(models.Model):
    """Model to store multiple related pages for a DawsonCard."""

    card = ParentalKey(
        "SimpleCard", related_name="related_pages", on_delete=models.CASCADE
    )
    display_title = models.CharField(
        max_length=255,
        help_text="Optional title to display in link",
        blank=True,
    )
    related_page = models.ForeignKey(
        "EnhancedStandardPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional URL to link to when the card is clicked.",
    )

    panels = [
        FieldPanel("display_title"),
        PageChooserPanel("related_page"),
        FieldPanel("url"),
    ]


@register_snippet
class SimpleCard(ClusterableModel):
    """A Simple Card that contains optional title, icon, and related pages."""

    parent_page = ParentalKey(
        "SimpleCardGroup", related_name="cards", on_delete=models.CASCADE
    )

    card_title = models.CharField(
        max_length=255,
        null=True,
        blank="True",
        help_text="The title to appear at the top of the card",
    )
    card_icon = models.CharField(
        max_length=200,
        null=True,
        blank="True",
        help_text='Icon Name - see https://fontawesome.com/icons/ and enter the name of the icon (i.e. "accessible")',
    )

    # Define panels for the admin interface
    panels = [
        FieldPanel("card_title"),
        FieldPanel("card_icon"),
        InlinePanel("related_pages", label="Related Pages"),
    ]

    def __str__(self):
        return (
            self.card_title
            if self.card_title
            else f"Simple Card - {self.parent_page.group_label or self.parent_page.parent_page.title}"
        )

    class Meta:
        ordering = ["id"]


@register_snippet
class FancyCard(ClusterableModel):
    parent_page = ParentalKey(
        "DawsonPage", related_name="fancy_card", on_delete=models.CASCADE
    )

    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image to display with in dark blue card.",
    )

    url = models.CharField(
        max_length=255,
        null=True,
        blank="True",
        help_text="The URL to link to when the photo is clicked.",
    )

    text = models.CharField(
        max_length=255,
        null=True,
        blank="True",
        help_text="The text to appear next to the image in the light blue card.",
    )

    def __str__(self):
        return f"Fancy Card - {self.parent_page.title}"


class SimpleCardGroup(ClusterableModel):
    """Group model for dynamically grouping Simple Cards."""

    parent_page = ParentalKey(
        "DawsonPage", related_name="card_groups", on_delete=models.CASCADE
    )

    group_label = models.CharField(
        blank=True,
        max_length=255,
        help_text="Label for this group of cards (e.g., 'Section 1: Featured Cards').",
    )

    panels = [
        FieldPanel("group_label"),
        InlinePanel("cards", label="Cards in this Group"),
    ]

    def __str__(self):
        return (
            self.group_label
            if self.group_label
            else f"Simple Card -{self.parent_page.title}"
        )


class PhotoDedication(models.Model):
    """Model to store data for a dedication."""

    dawson_page = ParentalKey(
        "DawsonPage",
        related_name="photo_dedication",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    enhanced_standard_page = ParentalKey(
        "EnhancedStandardPage",
        related_name="photo_dedications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255,
        help_text="Enter the title for the dedication",
    )

    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image to display with this dedication",
    )

    paragraph_text = RichTextField(
        blank=True,
        help_text="Add the main paragraph text for the dedication section",
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Enter alternative text for the image",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("photo"),
        FieldPanel("paragraph_text"),
    ]


class Meta:
    verbose_name = "Photo Dedication"
    verbose_name_plural = "Photo Dedication"


class DawsonPage(StandardPage):
    """Page model for Dawson eFiling Page."""

    content_panels = StandardPage.content_panels + [
        InlinePanel("fancy_card", label="Full Width Card Sections"),
        InlinePanel("card_groups", label="Card Sections"),
        InlinePanel("photo_dedication", label="Photo Dedication"),
    ]


class RedirectPage(StandardPage):
    content_panels = StandardPage.content_panels
