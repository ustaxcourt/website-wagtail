from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable, ParentalKey
from django.utils import timezone


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("images", label="Full Width Carousel Image"),
        InlinePanel("entries", label="Entries"),
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


class HomePageEntry(Orderable):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=2000, blank=True)
    body = RichTextField(blank=True)
    id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    persist_to_press_releases = models.BooleanField(default=True)

    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("persist_to_press_releases"),
    ]
