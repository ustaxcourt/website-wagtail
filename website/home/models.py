from django.db import models
from django import forms
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from django.conf import settings

from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("entries", label="Entries"),
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


class HomePageEntry(models.Model):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
    ]
