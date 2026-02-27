from home.models.pages.standard import StandardPage
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import ParentalKey, Orderable
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.common import custom_promote_panels
from django.db import models


class PamphletsPage(StandardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    content_panels = StandardPage.content_panels + [
        InlinePanel("entries", label="Entries"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels,
        promote_panels=custom_promote_panels,
        settings_panels=StandardPage.settings_panels,
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        entries = self.entries.all()
        context["entries"] = entries
        return context


class PamphletEntry(Orderable):
    title = models.CharField(max_length=255)
    pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    code = models.CharField(verbose_name="Page Range", max_length=255, blank=True)
    date_range = models.CharField(verbose_name="Date Range", max_length=255)
    citation = RichTextField(verbose_name="Cases", blank=True)

    parentpage = ParentalKey(
        "PamphletsPage", related_name="entries", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("pdf"),
        FieldPanel("code"),
        FieldPanel("date_range"),
        FieldPanel("citation"),
    ]
