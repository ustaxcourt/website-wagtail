from home.models.pages.standard import StandardPage
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import ParentalKey
from django.db import models


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
