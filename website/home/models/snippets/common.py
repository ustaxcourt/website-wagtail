from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin, PageQuerySet, WorkflowMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.snippets.models import register_snippet
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitSnippetForm
from wagtail.snippets.views.snippets import SnippetViewSet


class CommonText(
    ModerationMixin, WorkflowMixin, DraftStateMixin, RevisionMixin, models.Model
):
    name = models.CharField(
        max_length=255, help_text="Name of the text snippet", blank=False
    )
    text = RichTextField(help_text="HTML Rich text content", blank=False)
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="commontext"
    )
    objects = PageQuerySet.as_manager()

    content_panels = [
        FieldPanel("name"),
        FieldPanel("text"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    def __str__(self):
        return self.name

    @property
    def revisions(self):
        return self._revisions


class CommonTextViewSet(SnippetViewSet):
    model = CommonText
    form_class = ReviewByRequiredOnSubmitSnippetForm
    # Uses CommonText.edit_handler for UI


register_snippet(CommonTextViewSet)
