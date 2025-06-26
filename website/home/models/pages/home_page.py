from django.db import models
from django.contrib import messages

from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable, ParentalKey
from wagtail.search import index

from django.utils import timezone
from ..custom_blocks.add_entry_custom_button import AddEntryButton


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("images", label="Full Width Carousel Image"),
        InlinePanel("entries", label="Entries"),
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

    def add_entry_above_me(self, sort_order, request):
        try:
            parent = self.homepage.get_latest_revision_as_object()

            new_entry = HomePageEntry(
                homepage=parent,
                title="Insert title ...",
                body="",
                start_date=None,
                end_date=None,
                persist_to_press_releases=True,
            )

            entries = list(parent.entries.order_by("sort_order"))
            current_index = sort_order

            if current_index > -1:
                for i in range(len(entries) - 1, current_index - 1, -1):
                    entry = parent.entries.get(sort_order=i)
                    parent.entries.remove(entry)
                    entry.sort_order += 1
                    parent.entries.add(entry)

                new_entry.sort_order = current_index
                parent.entries.add(new_entry)
                parent.save_revision(user=request.user)

            return new_entry
        except Exception as e:
            messages.error(request, f"Error adding entry above: {str(e)}")
            return None

    panels = [
        AddEntryButton(button_text="Add Entry Above"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("persist_to_press_releases"),
    ]
