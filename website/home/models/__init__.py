from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from django.core.exceptions import ValidationError
from wagtail.models import Orderable
from datetime import date

from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.blocks import PageChooserBlock
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.models import DraftStateMixin, LockableMixin, RevisionMixin
from wagtail.models import PreviewableMixin
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import render
from django.http import Http404
from wagtail.blocks import RawHTMLBlock
from wagtail.blocks import DateBlock
import logging


from home.models.judges import (
    JudgeCollection,  # noqa: F401
    JudgeProfile,
    JudgeRole,
)
from home.models.settings import (
    Footer,  # noqa: F401
    GoogleAnalyticsSettings,  # noqa: F401
)
from home.models.config import IconCategories  # noqa: F401
from home.models.snippets.navigation import (
    NavigationRibbon,  # noqa: F401
    NavigationRibbonLink,  # noqa: F401
)
from home.models.snippets.common import CommonText  # noqa: F401
from home.models.pages.standard import StandardPage
from home.models.custom_blocks.photo_dedication import PhotoDedicationBlock  # noqa: F401
from home.models.custom_blocks.common import CommonBlock, link_obj, ColumnBlock  # noqa: F401
from home.models.custom_blocks.alert_message import AlertMessageBlock  # noqa: F401
from home.models.custom_blocks.button import ButtonBlock  # noqa: F401
from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.models.pages.enhanced_standard import IndentStyle  # noqa: F401
from home.models.pages.trial import PlacesOfTrialPage  # noqa: F401
from home.models.pages.pamphlet import PamphletsPage, PamphletEntry  # noqa: F401
from home.models.pages.release_notes import ReleaseNotes  # noqa: F401
from home.models.pages.internship import InternshipPrograms  # noqa: F401
from home.models.pages.press_release import PressReleasePage  # noqa: F401
from home.models.pages.home_page import HomePage, HomePageEntry, HomePageImage  # noqa: F401

logger = logging.getLogger(__name__)


judge_snippet = SnippetChooserBlock(
    target_model="home.JudgeCollection",
    required=False,
    help_text="Optionally pick a JudgeCollection snippet",
    label="Judge Collection",
)


class JudgeColumnBlock(CommonBlock):
    judgeCollection = judge_snippet


class JudgeColumns(blocks.StructBlock):
    column = blocks.ListBlock(JudgeColumnBlock())


class JudgeIndex(RoutablePageMixin, Page):
    """
    A specialized page for displaying judges categorized by their titles.
    Only one instance of this page can exist in the site.
    """

    template = "home/enhanced_standard_page.html"
    max_count = 1

    body = StreamField(
        [
            ("columns", JudgeColumns()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Add judge profiles or collections to display on this page",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Get all judge collections
        roles = JudgeRole.objects.filter(
            role_name__in=["Chief Judge", "Chief Special Trial Judge"]
        )
        context["roles"] = roles
        return context

    @route(r"^(?P<id>\d+)/(?P<last_name>[\w-]+)/$")
    def judge_detail(self, request, id, last_name):
        try:
            # Use the ID to find the judge
            judge = JudgeProfile.objects.get(id=id)
            context = self.get_context(request)
            context["judge"] = judge
            if judge.last_name.lower() != last_name:
                raise Http404("Judge not found")
            return render(request, "home/judge_detail.html", context)
        except JudgeProfile.DoesNotExist:
            # Handle case where judge doesn't exist
            raise Http404("Judge not found")

    class Meta:
        verbose_name = "Judges Index Page"
        abstract = False


class CaseRelatedFormsPage(StandardPage):
    content_panels = Page.content_panels + [
        InlinePanel("forms", label="Forms"),
    ]


class CaseRelatedFormsEntry(models.Model):
    formName = models.CharField(max_length=255)
    pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    number = models.CharField(max_length=255, blank=True)
    formNameNote = models.CharField(max_length=255, blank=True)
    eligibleForEFilingByPetitioners = models.CharField(max_length=255)
    eligibleForEFilingByPractitioners = models.CharField(max_length=255)

    parentpage = ParentalKey(
        "CaseRelatedFormsPage", related_name="forms", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("formName"),
        FieldPanel("formNameNote"),
        FieldPanel("pdf"),
        FieldPanel("number"),
        FieldPanel("eligibleForEFilingByPetitioners"),
        FieldPanel("eligibleForEFilingByPractitioners"),
    ]


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


class PDFs(Orderable):
    page = ParentalKey(
        "AdministrativeOrdersPage", related_name="pdfs", on_delete=models.CASCADE
    )

    pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("pdf"),
    ]


class AdministrativeOrdersPage(StandardPage):
    content_panels = StandardPage.content_panels + [
        InlinePanel("pdfs", label="PDFs"),
    ]


class VacancyAnnouncementsPage(StandardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        today = date.today()
        active_vacancies = VacancyEntry.objects.filter(
            parentpage=self, closing_date__gte=today
        ).order_by("closing_date")
        context["active_vacancies"] = active_vacancies
        return context

    content_panels = Page.content_panels + [
        InlinePanel("vacancies", label="Vacancies"),
    ]


class VacancyEntry(Orderable):
    parentpage = ParentalKey(
        "VacancyAnnouncementsPage", related_name="vacancies", on_delete=models.CASCADE
    )

    number = models.CharField(max_length=50, help_text="Vacancy announcement number")
    position_title = models.CharField(
        max_length=255, help_text="Position title, series, and grade"
    )
    closing_date = models.DateField(help_text="Closing date for the vacancy")
    url = models.URLField(max_length=255, help_text="Link to the vacancy announcement")

    panels = [
        FieldPanel("number"),
        FieldPanel("position_title"),
        FieldPanel("closing_date"),
        FieldPanel("url"),
    ]

    def clean(self):
        super().clean()
        # Check if closing_date is before today
        if self.closing_date and self.closing_date < date.today():
            raise ValidationError(
                {"closing_date": "Closing date cannot be in the past."}
            )

    class Meta:
        ordering = ["closing_date"]

    def is_active(self):
        return self.closing_date >= date.today()


class SubNavigationLinkBlock(blocks.StructBlock):
    """Represents a sub-navigation link that can point to internal or external pages"""

    title = blocks.CharBlock(
        required=True, help_text="Display text for the navigation link"
    )
    page = PageChooserBlock(required=False, help_text="Select a page to link to")
    external_url = blocks.URLBlock(required=False, help_text="Or enter an external URL")

    class Meta:
        icon = "link"


@register_snippet
class NavigationMenu(
    PreviewableMixin, DraftStateMixin, LockableMixin, RevisionMixin, ClusterableModel
):
    def clean(self):
        super().clean()
        # Check if another menu already exists during creation
        if not self.pk and NavigationMenu.objects.exists():
            raise ValidationError("Only one Navigation Menu can exist in the system.")

    menu_items = StreamField(
        [
            (
                "section",
                blocks.StructBlock(
                    [
                        (
                            "title",
                            blocks.CharBlock(
                                required=True, help_text="Top level navigation title"
                            ),
                        ),
                        (
                            "external_url",
                            blocks.URLBlock(
                                required=False, help_text="Or enter an external URL"
                            ),
                        ),
                        ("sub_links", blocks.ListBlock(SubNavigationLinkBlock())),
                    ]
                ),
            )
        ],
        use_json_field=True,
        blank=True,
    )

    def get_preview_template(self, request, mode_name):
        return "previews/header_preview.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["self"] = self
        return context

    # Required for RevisionMixin
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="navigation_menu"
    )

    panels = [
        FieldPanel("menu_items"),
    ]

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Navigation Menu"
        verbose_name_plural = "Navigation Menus"

    def __str__(self):
        return "Navigation Menu"

    @classmethod
    def get_active_menu(cls):
        return cls.objects.filter(live=True).first()


class EnhancedRawHTMLPage(EnhancedStandardPage):
    """
    A specialized page type that allows embedding raw HTML.
    """

    template = "home/enhanced_standard_page.html"

    raw_html_body = StreamField(
        [
            ("raw_html", RawHTMLBlock(label="Raw HTML")),
            (
                "questionanswers",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("question", blocks.CharBlock(required=False)),
                            (
                                "answer",
                                blocks.StructBlock(
                                    [
                                        (
                                            "rich_text",
                                            blocks.RichTextBlock(required=False),
                                        ),
                                        (
                                            "html_block",
                                            blocks.RawHTMLBlock(required=False),
                                        ),
                                    ],
                                    required=False,
                                ),
                            ),
                            ("anchortag", blocks.CharBlock(required=False)),
                        ]
                    ),
                    label="Question and Answer",
                    help_text="Add a question and answer with anchor tag for linking",
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("raw_html_body"),
    ]

    class Meta:
        verbose_name = "Enhanced Raw HTML Page"


class DirectoryColumnBlock(CommonBlock):
    JudgeCollection = judge_snippet  # noqa: F811
    DirectoryEntry = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("description", blocks.RichTextBlock()),
                ("phone_number", blocks.CharBlock()),
            ]
        )
    )


class DirectoryIndex(Page):
    template = "home/enhanced_standard_page.html"
    max_count = 1

    body = StreamField(
        [
            ("directory", DirectoryColumnBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Directory entries or judge profiles",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("body"),
    ]


class JudgesRecruiting(EnhancedStandardPage):
    judges_recruiting = StreamField(
        [
            (
                "message",
                blocks.RichTextBlock(
                    required=False,
                    help_text="Default message to display when no judges are recruiting.",
                ),
            ),
            (
                "judge",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            (
                                "judge_name",
                                SnippetChooserBlock(
                                    "home.JudgeProfile", required=False
                                ),
                            ),
                            ("description", blocks.RichTextBlock(blank=True)),
                            (
                                "apply_to_email",
                                blocks.CharBlock(
                                    required=False,
                                    help_text="Enter a valid email.",
                                ),
                            ),
                            (
                                "display_from",
                                DateBlock(
                                    required=False,
                                    help_text="Start displaying from this date",
                                ),
                            ),
                            (
                                "display_to",
                                DateBlock(
                                    required=False,
                                    help_text="Stop displaying after this date",
                                ),
                            ),
                        ]
                    ),
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        help_text="Add judges recruiting details",
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("judges_recruiting"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        today = date.today()
        # Filter the StreamField content for active judges
        filtered_judges = []
        for block in self.judges_recruiting:
            if block.block_type == "judge":
                for judge in block.value:
                    display_from = judge.get("display_from")
                    display_to = judge.get("display_to")
                    if (not display_from or display_from <= today) and (
                        not display_to or display_to >= today
                    ):
                        filtered_judges.append(judge)
            elif block.block_type == "message":
                message = block.value
                context["message"] = message
        context["judges_recruiting"] = filtered_judges
        return context


class CSVUploadPage(EnhancedStandardPage):
    csv_file = models.FileField(upload_to="csv_files/")

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("csv_file"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if self.csv_file:
            csv_data = self.get_csv_data()
            if csv_data["headers"] and csv_data["rows"]:
                context["csv_data"] = csv_data
            else:
                context["csv_data"] = None  # Explicitly set to None if no data
        else:
            context["csv_data"] = None
        return context

    def get_csv_data(self):
        import csv
        from io import StringIO

        csv_data = {"headers": [], "rows": []}

        # Open the file and read it
        with self.csv_file.open("r") as file:
            content = file.read()
        if isinstance(content, bytes):  # Check if data is in bytes
            content = content.decode("utf-8")  # Decode bytes to string
        csv_file = StringIO(content)

        # Parse the CSV
        csv_reader = csv.reader(csv_file)

        # Get headers from the first row
        try:
            csv_data["headers"] = next(csv_reader)
            csv_data["rows"] = [row for row in csv_reader]
        except StopIteration:
            # Handle empty CSV
            pass
        finally:
            pass
        return csv_data
