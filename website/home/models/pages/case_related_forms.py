from django.db import models
from wagtail.models import Page, ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from home.models.custom_blocks.common import custom_promote_panels
from home.admin.moderation import ModerationTabbedInterface


from home.models.pages.standard import StandardPage


class CaseRelatedFormsPage(StandardPage):
    show_floating_definitions_button = models.BooleanField(
        default=False,
        verbose_name="Floating Definitions Button",
        help_text="Check to display the floating definitions button on this page.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("show_floating_definitions_button"),
        InlinePanel("forms", label="Forms"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels,
        promote_panels=custom_promote_panels,
        settings_panels=StandardPage.settings_panels,
    )


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
