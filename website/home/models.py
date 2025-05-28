from django import forms
from django.conf import settings
from django.db import models
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from django.core.exceptions import ValidationError
from wagtail.models import Orderable
from datetime import date, datetime

from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.blocks import PageChooserBlock
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.models import DraftStateMixin, LockableMixin, RevisionMixin
from wagtail.models import PreviewableMixin
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import render
from django.utils import timezone
from django.http import Http404
from wagtail.blocks import RawHTMLBlock
from wagtail.blocks import DateBlock
from collections import defaultdict
from operator import itemgetter
from django.template.response import TemplateResponse
from django.utils.html import strip_tags
import logging
import re
import os


from home.common_models.judges import (
    JudgeCollection,  # noqa: F401
    JudgeProfile,
    JudgeRole,
)

logger = logging.getLogger(__name__)


table_value_types = [
    ("text", blocks.RichTextBlock()),
]


@register_setting
class Footer(BaseGenericSetting):
    technicalQuestions = RichTextField(
        blank=True, help_text="Content for technical questions."
    )
    otherQuestions = RichTextField(blank=True, help_text="Content for other questions.")

    content_panels = Page.content_panels + [
        FieldPanel("technicalQuestions"),
        FieldPanel("otherQuestions"),
    ]


@register_setting
class GoogleAnalyticsSettings(BaseGenericSetting):
    tracking_id = models.CharField(
        max_length=20,
        help_text="Google Analytics Measurement ID (e.g., G-1234567890)",
        default=settings.GOOGLE_ANALYTICS_ID,
    )

    panels = [
        FieldPanel(
            "tracking_id",
            widget=forms.TextInput(attrs={"value": settings.GOOGLE_ANALYTICS_ID}),
        ),
    ]


class IndentStyle(models.TextChoices):
    INDENTED = "indented"
    UNINDENTED = "unindented"


LIST_TYPE_CHOICES = [
    ("ordered", "Ordered List"),
    ("unordered", "Unordered List"),
]

LIST_TYPE_BLOCK = blocks.ChoiceBlock(
    choices=LIST_TYPE_CHOICES, required=False, default="ordered"
)


class IconCategories(models.TextChoices):
    NONE = ("",)
    BOOK = "fa-solid fa-book"
    BUILDING_BANK = "fa-solid fa-building-columns"
    CALENDAR_MONTH = "fa-solid fa-calendar"
    CHEVRON_RIGHT = "fa-solid fa-chevron-right"
    FILE = "fa-solid fa-file"
    HAMMER = "fa-solid fa-gavel"
    INFO = "fa-solid fa-circle-info"
    CHECK = "fa-solid fa-check"
    LINK = "fa-solid fa-link"
    EXCLAMATION_MARK = "fa-solid fa-exclamation"
    PDF = "fa-solid fa-file-pdf"
    SCALE = "fa-solid fa-scale-balanced"
    USER = "fa-solid fa-user"
    VIDEO = "fa-solid fa-video"
    SETTINGS = "fa-solid fa-gear"
    BRIEFCASE = "fa-solid fa-briefcase"
    SEARCH = "fa-solid fa-magnifying-glass"


class StandardPage(Page):
    class Meta:
        abstract = False

    body = RichTextField(blank=True, help_text="Insert text here.")

    content_panels = Page.content_panels + [FieldPanel("body")]


class NavigationRibbonLink(models.Model):
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=200, choices=IconCategories.choices)
    url = models.CharField(max_length=1000)

    navigation_ribbon = ParentalKey(
        "NavigationRibbon", related_name="links", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("icon"),
        FieldPanel("url"),
    ]


@register_snippet
class NavigationRibbon(ClusterableModel):
    name = models.CharField(max_length=255)

    panels = [
        InlinePanel("links", label="Links"),  # Now properly references the ParentalKey
    ]

    def __str__(self):
        return self.name


@register_snippet
class CommonText(models.Model):
    name = models.CharField(
        max_length=255, help_text="Name of the text snippet", blank=False
    )
    text = RichTextField(help_text="HTML Rich text content", blank=False)

    panels = [
        FieldPanel("name"),
        FieldPanel("text"),
    ]

    def __str__(self):
        return self.name


class PhotoDedicationBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=True)
    photo = ImageBlock(
        required=False, help_text="Upload an image to display with this dedication"
    )
    paragraph_text = blocks.RichTextBlock(
        required=False,
        help_text="Add the main paragraph text for the dedication section",
    )
    alt_text = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Provide alternative text for the image for accessibility.",
    )

    class Meta:
        icon = "image"
        label = "Photo Dedication"


link_obj = blocks.ListBlock(
    blocks.StructBlock(
        [
            ("title", blocks.CharBlock()),
            (
                "icon",
                blocks.ChoiceBlock(
                    choices=[
                        (
                            icon.value,
                            icon.name.replace("_", " ").title(),
                        )
                        for icon in IconCategories
                    ],
                    required=False,
                ),
            ),
            (
                "document",
                DocumentChooserBlock(required=False),
            ),
            (
                "video",
                DocumentChooserBlock(required=False),
            ),
            ("url", blocks.CharBlock(required=False)),
            (
                "text_only",
                blocks.BooleanBlock(required=False),
            ),
        ]
    )
)


class CommonBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(label="Heading 2")
    h3 = blocks.CharBlock(label="Heading 3")
    hr = blocks.BooleanBlock(
        label="Horizontal Rule",
        default=True,
        help_text="Add Horizontal Rule.",
    )
    h2WithAnchorTag = blocks.StructBlock(
        [
            ("text", blocks.CharBlock()),
            ("anchortag", blocks.CharBlock(required=False)),
        ],
        label="Heading 2 with Anchor Tag",
        help_text="Heading 2 with optional anchor tag for linking",
    )
    clickableButton = blocks.StructBlock(
        [
            ("text", blocks.CharBlock()),
            ("url", blocks.CharBlock(required=False)),
        ],
        label="Clickable Button",
    )
    links = blocks.StructBlock(
        [
            (
                "class",
                blocks.ChoiceBlock(
                    choices=[
                        ("indented", "Indented"),
                        ("unindented", "Unindented"),
                    ],
                    default="indented",
                ),
            ),
            # Reuse your link_obj here
            ("links", link_obj),
        ],
        label="Links",
    )


class ColumnBlock(blocks.StructBlock):
    column = blocks.ListBlock(CommonBlock())


def create_nested_list_block(max_depth=5, current_depth=1):
    """
    Creates a nested list block structure with configurable depth.

    Args:
        max_depth (int): Maximum nesting depth allowed (default: 4)
        current_depth (int): Current depth in the recursion (used internally)

    Returns:
        blocks.StructBlock: A Wagtail block structure for nested lists
    """
    # Base structure that's common at all levels
    list_item_blocks = [
        ("text", blocks.RichTextBlock(required=False)),
        ("image", ImageBlock(required=False)),
    ]

    # Add nested_list field if we haven't reached max depth
    if current_depth < max_depth:
        list_item_blocks.append(
            (
                "nested_list",
                blocks.ListBlock(
                    create_nested_list_block(max_depth, current_depth + 1),
                    default=[],
                ),
            )
        )

    return blocks.StructBlock(
        [
            ("list_type", LIST_TYPE_BLOCK),
            (
                "items",
                blocks.ListBlock(
                    blocks.StructBlock(list_item_blocks, required=False),
                    default=[],
                ),
            ),
        ],
        required=False,
    )


class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text="Button text")
    href = blocks.CharBlock(
        required=True, help_text="Button link  (Can be relative or absolute)"
    )
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
        ],
        default="primary",
        help_text="Choose the button style",
    )

    class Meta:
        icon = "placeholder"
        label = "Button"


class AlertMessageBlock(blocks.StructBlock):
    message = blocks.RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        icon = "warning"
        label = "Alert Message"


class EnhancedStandardPage(Page):
    class Meta:
        verbose_name = "Enhanced Standard Page"

    navigation_ribbon = models.ForeignKey(
        NavigationRibbon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    body = StreamField(
        [
            (
                "heading",
                blocks.StructBlock(
                    [
                        ("text", blocks.CharBlock()),
                        (
                            "level",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("h2", "Heading 2"),
                                    ("h3", "Heading 3"),
                                    ("h4", "Heading 4"),
                                    ("h5", "Heading 5"),
                                ]
                            ),
                        ),
                        (
                            "id",
                            blocks.CharBlock(
                                required=False,
                                help_text="Optional ID for linking to this heading",
                            ),
                        ),
                    ]
                ),
            ),
            ("h2", blocks.CharBlock(label="Heading 2")),
            ("h3", blocks.CharBlock(label="Heading 3")),
            ("h4", blocks.CharBlock(label="Heading 4")),
            ("paragraph", blocks.RichTextBlock()),
            ("snippet", SnippetChooserBlock("home.CommonText")),
            ("button", ButtonBlock()),
            (
                "hr",
                blocks.BooleanBlock(
                    label="Horizontal Rule",
                    default=True,
                    help_text="Add 'Horizontal Rule'.",
                ),
            ),
            (
                "iframe",
                blocks.StructBlock(
                    [
                        ("src", blocks.URLBlock(required=True)),
                        ("width", blocks.CharBlock(required=True)),
                        ("height", blocks.CharBlock(required=True)),
                        ("class", blocks.CharBlock(required=False)),
                        ("loading", blocks.CharBlock(required=False)),
                        ("data_delay", blocks.CharBlock(required=False)),
                        ("name", blocks.CharBlock(required=False)),
                        ("title", blocks.CharBlock(required=False)),
                    ]
                ),
            ),
            (
                "alert",
                blocks.StructBlock(
                    [
                        (
                            "alert_type",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("info", "Info"),
                                    ("success", "Success"),
                                ],
                                default="info",
                            ),
                        ),
                        ("content", blocks.RichTextBlock()),
                    ],
                ),
            ),
            ("image", ImageBlock()),
            ("photo_dedication", PhotoDedicationBlock()),
            (
                "table",
                TypedTableBlock(
                    table_value_types,
                ),
            ),
            (
                "unstyled_table",
                TypedTableBlock(table_value_types),
            ),
            ("list", create_nested_list_block(max_depth=4)),
            (
                "links",
                blocks.StructBlock(
                    [
                        (
                            "class",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("indented", IndentStyle.INDENTED),
                                    ("unindented", IndentStyle.UNINDENTED),
                                ],
                                default=IndentStyle.INDENTED,
                            ),
                        ),
                        ("links", link_obj),
                    ]
                ),
            ),
            (
                "questionanswers",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("question", blocks.CharBlock(required=False)),
                            ("answer", blocks.RichTextBlock()),
                            ("anchortag", blocks.CharBlock()),
                        ]
                    ),
                    label="Question and Answer",
                    help_text="Add a question and answer with anchor tag for linking",
                ),
            ),
            ("columns", ColumnBlock()),
            (
                "embedded_video",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(required=False)),
                        ("description", blocks.RichTextBlock(required=False)),
                        ("video_url", blocks.URLBlock(required=False)),
                    ]
                ),
            ),
            (
                "card",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            (
                                "icon",
                                blocks.ChoiceBlock(
                                    choices=[
                                        (
                                            icon.value,
                                            icon.name.replace("_", " ").title(),
                                        )
                                        for icon in IconCategories
                                    ],
                                    required=True,
                                ),
                            ),
                            ("title", blocks.CharBlock(required=True)),
                            ("description", blocks.RichTextBlock(required=True)),
                            (
                                "color",
                                blocks.ChoiceBlock(
                                    choices=[
                                        ("green", "Green"),
                                        ("yellow", "Yellow"),
                                    ],
                                    required=True,
                                ),
                            ),
                        ],
                        label="Card",
                    ),
                    label="Card Set",
                ),
            ),
        ],
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("navigation_ribbon"),
        FieldPanel("body"),
    ]


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


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("images", label="Full Width Carousel Image"),
        InlinePanel("entries", label="Entries"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["now"] = timezone.now()
        live_entries = HomePageEntry.objects.filter(homepage=self).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
        )
        context["entries"] = live_entries
        return context


class HomePageImage(Orderable):
    page = ParentalKey("HomePage", related_name="images", on_delete=models.CASCADE)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("image"),
    ]


class HomePageEntry(Orderable):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=2000, blank=True)
    body = RichTextField(blank=True)
    id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    persist_to_press_releases = models.BooleanField(default=True)

    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("persist_to_press_releases"),
    ]


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


class PamphletsPage(StandardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    content_panels = StandardPage.content_panels + [
        InlinePanel("entries", label="Entries"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        entries = PamphletEntry.objects.all().order_by("-volume_number")
        context["entries"] = entries
        return context


class PamphletEntry(models.Model):
    title = models.CharField(max_length=255)
    pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    code = models.CharField(max_length=255, blank=True)
    date_range = models.CharField(max_length=255)
    citation = RichTextField(blank=True)
    volume_number = models.FloatField(default=0)

    parentpage = ParentalKey(
        "PamphletsPage", related_name="entries", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("pdf"),
        FieldPanel("code"),
        FieldPanel("date_range"),
        FieldPanel("citation"),
        FieldPanel("volume_number"),
    ]


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


class InternshipSectionBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(form_classname="title")
    paragraph = blocks.RichTextBlock()


class InternshipPositionBlock(blocks.StructBlock):
    description = blocks.RichTextBlock(required=False)
    section = InternshipSectionBlock(required=False)
    paragraph = blocks.RichTextBlock(
        required=False, help_text="A simple paragraph of text."
    )
    display_from = blocks.DateBlock(
        required=False, help_text="Start displaying this internship"
    )
    closing_date = blocks.DateBlock(
        required=False, help_text="Closing date for this internship"
    )
    external_link = blocks.URLBlock(
        required=False, help_text="Link to external internship posting"
    )

    class Meta:
        label = "Internship Position"
        icon = "user"


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


def extract_pdf_filename_from_body(html):
    """Extracts the .pdf filename from an anchor tag's href in the HTML string. Returns the filename (e.g., '04072025.pdf') or None."""
    match = re.search(r'href="([^"]+\.pdf)"', html or "", re.IGNORECASE)
    if match:
        pdf_url = match.group(1)
        return os.path.basename(pdf_url)  # Extract just the filename
    return None


class PressReleasePage(RoutablePageMixin, EnhancedStandardPage):
    """
    A specialized page for managing press releases with grouping and archive routing.
    """

    press_release_body = StreamField(
        [
            ("button", ButtonBlock()),
            (
                "press_releases",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("release_date", blocks.DateBlock(required=False)),
                            (
                                "details",
                                blocks.StructBlock(
                                    [
                                        (
                                            "description",
                                            blocks.TextBlock(required=False),
                                        ),
                                        ("file", DocumentChooserBlock(required=False)),
                                    ],
                                    required=False,
                                ),
                            ),
                        ]
                    )
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        null=True,
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("press_release_body"),
    ]

    @route("archives/")
    def archive_view(self, request):
        grouped = self.group_press_releases_by_year
        all_years = list(grouped.keys())
        archived_years = all_years[5:]  # After first 5 years
        archived_releases = {year: grouped[year] for year in archived_years}

        context = self.get_context(request)
        context["press_releases_by_year"] = archived_releases
        context["is_archive"] = True
        self.title = "Press Release Archive"
        return TemplateResponse(request, self.template, context)

    @property
    def group_press_releases_by_year(self):
        grouped = defaultdict(list)
        seen_press_release_keys = set()  # (title, pdf), (description, file)
        for block in self.press_release_body:
            if block.block_type == "press_releases":
                for release in block.value:
                    release_date = release.get("release_date")
                    # Normalize release_date to `date` type
                    release_date = (
                        release_date.date()
                        if isinstance(release_date, datetime)
                        else release_date
                    )
                    if release_date:
                        year = release_date.year
                        release[
                            "release_date"
                        ] = release_date  # Ensure it stays consistent
                        grouped[year].append(release)

                        # Track for duplication prevention
                        details = release.get("details", {})
                        description = strip_tags(
                            details.get("description", "").strip().lower()
                        )
                        file = details.get("file")

                        if file and hasattr(file, "url"):
                            pdf_filename = os.path.basename(file.url).strip().lower()
                            seen_press_release_keys.add(("file", pdf_filename))

                            if description:
                                seen_press_release_keys.add(
                                    ("desc+file", description, pdf_filename)
                                )

        # Step 2: Add homepage entries, only if not duplicate
        persisted_entries = HomePageEntry.objects.filter(
            persist_to_press_releases=True, end_date__lt=timezone.now()
        ).order_by("-end_date")

        for entry in persisted_entries:
            pdf_url = extract_pdf_filename_from_body(entry.body)
            pdf_filename = os.path.basename(pdf_url).strip().lower() if pdf_url else ""
            title = entry.title.strip() if entry.title else ""
            is_duplicate = ("file", pdf_filename) in seen_press_release_keys or (
                "desc+file",
                title,
                pdf_filename,
            ) in seen_press_release_keys
            if is_duplicate:
                continue

            if not is_duplicate:
                release_date = entry.end_date.date() if entry.end_date else None
                year = release_date.year if release_date else "Unknown"
                grouped[year].append(
                    {
                        "is_homepage_entry": True,
                        "release_date": release_date,
                        "id": entry.id,
                        "title": entry.title,
                        "body": entry.body,
                        "file": pdf_filename,
                    }
                )
        # Sort releases in each year by descending date
        sorted_grouped = {
            year: sorted(releases, key=itemgetter("release_date"), reverse=True)
            for year, releases in grouped.items()
        }
        return dict(sorted(sorted_grouped.items(), reverse=True))

    def get_context(self, request):
        context = super().get_context(request)
        grouped = self.group_press_releases_by_year
        all_years = list(grouped.keys())
        first_five_years = all_years[:5]
        main_page_releases = {year: grouped[year] for year in first_five_years}
        context["press_releases_by_year"] = main_page_releases
        context["is_archive"] = False
        return context

    class Meta:
        verbose_name = "Press Release Page"


class ReleaseNotes(EnhancedStandardPage):
    """
    A page model for managing release notes with a title, paragraph, and a list of release entries.
    """

    paragraph = RichTextField(
        blank=True, help_text="Introduction or description for the release notes"
    )

    release_entries = StreamField(
        [
            (
                "release_entry",
                blocks.StructBlock(
                    [
                        (
                            "release_date",
                            blocks.DateBlock(
                                required=False, help_text="Date of the release"
                            ),
                        ),
                        (
                            "description",
                            blocks.RichTextBlock(
                                required=False,
                                help_text="Description or details of the release",
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="List of release entries with date and description",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("paragraph"),
        FieldPanel("release_entries"),
    ]

    class Meta:
        verbose_name = "Release Notes"
        verbose_name_plural = "Release Notes"


class InternshipPrograms(EnhancedStandardPage):
    internship_programs = StreamField(
        [
            ("h2", blocks.CharBlock(label="Heading 2")),
            ("paragraph", blocks.RichTextBlock()),
            ("internship", InternshipPositionBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Internship Programs Details",
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("internship_programs"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        today = date.today()

        filtered_blocks = []
        has_active_internship = False

        for block in self.internship_programs:
            if block.block_type == "internship":
                display_from = block.value.get("display_from")
                closing_date = block.value.get("closing_date")

                if display_from <= today and closing_date >= today:
                    has_active_internship = True
                    filtered_blocks.append(block)

            elif block.block_type in ["h2", "paragraph"]:
                filtered_blocks.append(block)

        if has_active_internship:
            context["active_internships"] = filtered_blocks
        else:
            context["active_internships"] = []
            context["no_opportunities_message"] = (
                "There are currently no internship opportunities at the Court. "
                "Please check back at a later time."
            )

        return context


class TrialCityBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    note = blocks.TextBlock(required=False)
    address = blocks.CharBlock(
        required=False, help_text="Street address or location name"
    )

    class Meta:
        icon = "home"
        label = "Trial City"


class TrialStateBlock(blocks.StructBlock):
    state = blocks.CharBlock()
    cities = blocks.ListBlock(TrialCityBlock())


class PlacesOfTrialPage(Page):
    places_of_trial = StreamField(
        [("state", TrialStateBlock())],
        use_json_field=True,
        blank=True,
    )
    body = StreamField(
        [
            ("text", blocks.RichTextBlock()),
            ("alert_message", AlertMessageBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("places_of_trial"),
    ]
