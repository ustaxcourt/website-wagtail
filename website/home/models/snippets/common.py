from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin, PageQuerySet
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class CommonText(DraftStateMixin, RevisionMixin, models.Model):
    name = models.CharField(
        max_length=255, help_text="Name of the text snippet", blank=False
    )
    text = RichTextField(help_text="HTML Rich text content", blank=False)
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="commontext"
    )
    objects = PageQuerySet.as_manager()

    panels = [
        FieldPanel("name"),
        FieldPanel("text"),
        PublishingPanel(),
    ]

    def __str__(self):
        return self.name

    @property
    def revisions(self):
        return self._revisions
