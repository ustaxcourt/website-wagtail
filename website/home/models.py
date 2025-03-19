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
from datetime import date

from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.blocks import PageChooserBlock


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


class NavigationCategories(models.TextChoices):
    NONE = "NONE", "None"
    ABOUT_THE_COURT = "ABOUT", "About the Court"
    RULES_AND_GUIDANCE = "RULES", "Rules & Guidance"
    ORDERS_AND_OPINIONS = "ORDERS", "Orders & Opinions"
    eFILING_AND_CASE_MAINTENANCE = "eFILING", "eFiling & Case Maintenance"


class IndentStyle(models.TextChoices):
    INDENTED = "indented"
    UNINDENTED = "unindented"


class IconCategories(models.TextChoices):
    NONE = ("",)
    BOOK_2 = "ti ti-book-2"
    BUILDING_BANK = "ti ti-building-bank"
    CALENDAR_MONTH = "ti ti-calendar-month"
    CHEVRON_RIGHT = "ti ti-chevron-right"
    FILE = "ti ti-file"
    HAMMER = "ti ti-hammer"
    INFO = "ti ti-info-circle"
    INFO_CIRCLE_FILLED = "ti ti-info-circle-filled"
    CHECK = "ti ti-check"
    LINK = "ti ti-link"
    EXCLAMATION_MARK = "ti ti-exclamation-mark"
    PDF = "ti ti-file-type-pdf"
    SCALE = "ti ti-scale"
    USER = "ti ti-user-filled"
    VIDEO = "ti ti-video-filled"
    SETTINGS = "ti ti-settings-filled"
    BRIEFCASE = "ti ti-briefcase-filled"
    SEARCH = "ti ti-search"


class NavigationMixin(Page):
    class Meta:
        abstract = True

    no_index = models.BooleanField(default=False)

    navigation_category = models.TextField(
        max_length=45,
        choices=NavigationCategories.choices,
        default=NavigationCategories.NONE,
    )

    redirectLink = models.CharField(
        blank=True, help_text="Insert link here.", max_length=250
    )

    menu_item_name = models.CharField(
        max_length=255,
        default="*NOT SET*",
        help_text="Enter the name of the page for the navigation bar link.",
    )

    promote_panels = Page.promote_panels + [
        FieldPanel("navigation_category", widget=forms.Select),
        FieldPanel("menu_item_name"),
        FieldPanel("redirectLink"),
    ]

    def clean(self):
        # Ensure 'search_description' is not empty
        super().clean()
        if not self.search_description:
            raise ValidationError({"search_description": "This field cannot be blank."})

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        navigation_sections = [
            {"title": label.upper(), "key": value}
            for value, label in NavigationCategories.choices
            if value != NavigationCategories.NONE
        ]
        context["navigation_sections"] = navigation_sections
        return context


class StandardPage(NavigationMixin):
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


class EnhancedStandardPage(NavigationMixin, Page):
    class Meta:
        abstract = False

    navigation_ribbon = models.ForeignKey(
        "NavigationRibbon",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    title_text = models.CharField(
        max_length=255, help_text="Title of the section", blank=True
    )
    description = RichTextField(blank=True, help_text="Description of the section")
    video_url = models.URLField(blank=True, help_text="YouTube embed URL")

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
            (
                "hr",
                blocks.BooleanBlock(
                    label="Horizontal Rule",
                    default=True,
                    help_text="Add 'Horizontal Rule'.",
                ),
            ),
            ("image", ImageBlock()),
            (
                "table",
                TypedTableBlock(
                    [
                        ("text", blocks.RichTextBlock()),
                    ]
                ),
            ),
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
        ]
    )
    content_panels = Page.content_panels + [
        FieldPanel("navigation_ribbon"),
        FieldPanel("body"),
    ]


class HomePage(NavigationMixin):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("images", label="Full Width Carousel Image"),
        InlinePanel("entries", label="Entries"),
    ]


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


class HomePageEntry(models.Model):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
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


class ExternalRedirectPage(NavigationMixin):
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

    panels = [
        FieldPanel("display_title"),
        PageChooserPanel("related_page"),
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
            else f"Simple Card {self.parent_page.group_label}"
        )


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
        return self.group_label


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


@register_setting
class NavigationMenu(BaseGenericSetting):
    """Represents the main navigation menu structure"""

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
                            "key",
                            blocks.CharBlock(
                                required=True,
                                help_text="Unique identifier for this section",
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

    panels = [
        FieldPanel("menu_items"),
    ]

    class Meta:
        verbose_name = "Navigation Menu"
