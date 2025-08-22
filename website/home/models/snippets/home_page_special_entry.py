from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from wagtail.search import index
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.fields import RichTextField
from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    WorkflowMixin,
    Orderable,
)


class HomePageSpecialEntry(
    Orderable,
    WorkflowMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
    title = models.CharField(max_length=2000, blank=True)
    body = RichTextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="homepagespecialentry"
    )

    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        PublishingPanel(),
    ]

    def __str__(self):
        return self.title or self.body[:50]

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Home Page Special Entry"
        verbose_name_plural = "Home Page Special Entries"
