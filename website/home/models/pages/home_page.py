from django.db import models

from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable, ParentalKey
from wagtail.search import index

from django.utils import timezone
from home.models import HomePageEntry


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("images", label="Full Width Carousel Image"),
        InlinePanel("entries", label="Entries", classname="inline-panel-no-add-button"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["now"] = timezone.now()
        live_entries = HomePageEntry.objects.filter(homepage=self).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
        )
        context["entries"] = live_entries
        return context


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
