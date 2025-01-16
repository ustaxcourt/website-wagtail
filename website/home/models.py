from django import forms
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from django.conf import settings


from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)

Page._meta.get_field("search_description").blank = False


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


class HomePage(Page):
    environment = settings.ENVIRONMENT
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("entries", label="Entries"),
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


class HomePageEntry(models.Model):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
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

    menu_item_name = models.CharField(
        max_length=255,
        default="*NOT SET*",
        help_text="Enter the name of the page for the navigation bar link.",
    )

    promote_panels = Page.promote_panels + [
        FieldPanel("navigation_category", widget=forms.Select),
        FieldPanel("menu_item_name"),
    ]


class StandardPage(NavigationMixin):
    class Meta:
        abstract = False

    body = RichTextField(blank=True, help_text="Insert text here.")

    content_panels = Page.content_panels + [FieldPanel("body")]


class CaseRelatedFormsPage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
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
