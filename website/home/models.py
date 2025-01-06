from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey

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


class HomePage(Page):
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
    number = models.CharField(max_length=255)
    formNameNote = models.CharField(max_length=255)
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
