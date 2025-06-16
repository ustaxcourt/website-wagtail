from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet
from wagtail.models import DraftStateMixin, RevisionMixin
from wagtail.admin.panels import PublishingPanel


@register_snippet
class ScheduledCommonText(DraftStateMixin, RevisionMixin, models.Model):
    body = RichTextField(verbose_name="Text")

    panels = [
        FieldPanel("body"),
        PublishingPanel(),
    ]

    def __str__(self):
        return f"Scheduled Text Snippet ({self.pk})"
