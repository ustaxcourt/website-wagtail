from django import forms
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from django.conf import settings
from django.core.exceptions import ValidationError
from wagtail.snippets.models import register_snippet
from wagtail.documents.widgets import AdminDocumentChooser
from modelcluster.models import ClusterableModel

from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)


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


class CaseRelatedFormsPage(StandardPage):
    content_panels = Page.content_panels + [
        InlinePanel("forms", label="Forms"),
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


class DawsonPage(StandardPage):
    pass


class CitationStyleManualPage(StandardPage):
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = StandardPage.content_panels + [
        FieldPanel("document"),
    ]


@register_snippet
class PDFListComponent(ClusterableModel):
    title = models.CharField(max_length=255, help_text="Title for the PDF list")

    panels = [
        FieldPanel("title"),
        InlinePanel("pdfs", label="PDF Documents"),
    ]

    def __str__(self):
        return self.title


class PDFDocument(models.Model):
    component = ParentalKey(
        PDFListComponent, on_delete=models.CASCADE, related_name="pdfs"
    )
    document = models.ForeignKey(
        "wagtaildocs.Document", on_delete=models.CASCADE, related_name="+"
    )
    description = models.CharField(
        max_length=255,
        help_text="Document description (e.g., 'Administrative Order 2024-01')",
    )

    panels = [
        FieldPanel("document", widget=AdminDocumentChooser),
        FieldPanel("description"),
    ]

    def __str__(self):
        return self.description
