from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.snippets.models import register_snippet
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.button import ButtonBlock
from wagtail.fields import StreamField

from django.contrib.contenttypes.fields import GenericRelation
from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    WorkflowMixin,
)


@register_snippet
class CallToActionBox(
    ModerationMixin, WorkflowMixin, DraftStateMixin, RevisionMixin, ClusterableModel
):
    header = models.CharField(
        max_length=255,
        help_text="Header to display in the Call to Action Box",
        blank=False,
    )
    body = models.CharField(
        max_length=500,
        help_text="Content to display in the Call to Action Box",
        blank=True,
        null=True,
    )
    buttons = StreamField(
        [("button", ButtonBlock())],
        use_json_field=True,
        blank=False,
        min_num=1,
        max_num=3,
        help_text="Buttons to display at the bottom of the Call to Action Box",
    )

    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="call_to_action_box"
    )

    content_panels = [
        FieldPanel("header"),
        FieldPanel("body"),
        FieldPanel("buttons"),
    ]
    panels = content_panels + [PublishingPanel()]

    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    def __str__(self):
        return self.header

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Call to Action Box"
        verbose_name_plural = "Call to Action Boxes"
