from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from django.db import models
from django.conf import settings
from django import forms


@register_setting
class Header(BaseGenericSetting):
    chief_judge = models.CharField(
        max_length=255,
        default="Patrick J. Urda, Chief Judge",
        help_text="Name and title of the Chief Judge",
    )
    clerk_of_court = models.CharField(
        max_length=255,
        default="Charles G. Jeane, Clerk of the Court",
        help_text="Name and title of the Clerk of the Court",
    )

    panels = [
        FieldPanel("chief_judge"),
        FieldPanel("clerk_of_court"),
    ]


@register_setting
class Footer(BaseGenericSetting):
    technicalQuestions = RichTextField(
        blank=True, help_text="Content for technical questions."
    )

    content_panels = Page.content_panels + [
        FieldPanel("technicalQuestions"),
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


@register_setting
class GoogleTagManagerSettings(BaseGenericSetting):
    gtm_container_id = models.CharField(
        max_length=32,
        blank=True,
        help_text="Google Tag Manager Container ID, e.g. GTM-XXXXXXX",
    )

    panels = [
        FieldPanel("gtm_container_id"),
    ]


@register_setting
class PrivateSeminarDisclosureSettings(BaseGenericSetting):
    """
    Site-wide settings for the Private Seminar Disclosures feature.
    Controls how long a disclosure remains visible on the public website.
    """

    disclosure_years = models.PositiveIntegerField(
        default=3,
        help_text=(
            "Number of years a seminar disclosure remains visible on the public website. "
            "Disclosures older than this are automatically hidden. Default: 3."
        ),
    )

    panels = [
        FieldPanel("disclosure_years"),
    ]

    class Meta:
        verbose_name = "Private Seminar Disclosure Settings"
