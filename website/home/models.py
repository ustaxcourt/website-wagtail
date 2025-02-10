from django import forms
from django.conf import settings
from django.db import models
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

from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageBlock
from wagtail.documents.blocks import DocumentChooserBlock


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
    INFO = "ti ti-info-circle"
    PDF = "ti ti-file-type-pdf"
    BOOK_2 = "ti ti-book-2"
    BUILDING_BANK = "ti ti-building-bank"
    HAMMER = "ti ti-hammer"
    SCALE = "ti ti-scale"
    CALENDAR_MONTH = "ti ti-calendar-month"
    FILE = "ti ti-file"
    INFO_CIRCLE_FILLED = "ti ti-info-circle-filled"
    CHEVRON_RIGHT = "ti ti-chevron-right"
    VIDEO = "ti ti-video-filled"


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


class EnhancedStandardPage(NavigationMixin):
    class Meta:
        abstract = False

    navigation_ribbon = models.ForeignKey(
        "NavigationRibbon",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    body = StreamField(
        [
            ("heading", blocks.CharBlock()),
            ("h3", blocks.CharBlock()),
            ("h4", blocks.CharBlock()),
            ("paragraph", blocks.RichTextBlock()),
            ("hr", blocks.BooleanBlock()),
            ("image", ImageBlock()),
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
                        (
                            "links",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        ("title", blocks.CharBlock()),
                                        (
                                            "icon",
                                            blocks.ChoiceBlock(
                                                choices=[
                                                    ("ti ti-file-type-pdf", "PDF"),
                                                    (
                                                        "ti ti-info-circle-filled",
                                                        "Info",
                                                    ),
                                                    ("ti ti-link", "Link"),
                                                ]
                                            ),
                                        ),
                                        (
                                            "document",
                                            DocumentChooserBlock(required=False),
                                        ),
                                        ("url", blocks.CharBlock(required=False)),
                                    ]
                                )
                            ),
                        ),
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
                        ]
                    )
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
        InlinePanel("entries", label="Entries"),
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
    related_page = models.ForeignKey(
        "StandardPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
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

    card = ParentalKey(
        "DawsonPage", related_name="photo_dedication", on_delete=models.CASCADE
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

    panels = [
        FieldPanel("title"),
        FieldPanel("photo"),
        FieldPanel("paragraph_text"),
    ]


class DawsonPage(StandardPage):
    """Page model for Dawson eFiling Page."""

    content_panels = StandardPage.content_panels + [
        InlinePanel("fancy_card", label="Full Width Card Sections"),
        InlinePanel("card_groups", label="Card Sections"),
        InlinePanel("photo_dedication", label="Photo Dedication"),
    ]


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
