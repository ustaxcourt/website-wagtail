from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.fields import RichTextField
from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    WorkflowMixin,
    Orderable,
    ParentalKey,
)


class HomePageEntry(
    Orderable, WorkflowMixin, DraftStateMixin, RevisionMixin, models.Model
):
    page = ParentalKey(
        "home.HomePage", related_name="entries", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=2000, blank=True)
    body = RichTextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    persist_to_press_releases = models.BooleanField(default=True)

    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="homepageentry"
    )

    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("persist_to_press_releases"),
        PublishingPanel(),
    ]

    def __str__(self):
        return self.title or "Untitled Entry"

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Home Page Entry"
        verbose_name_plural = "Home Page Entries"
