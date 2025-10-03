from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from modelcluster.models import ClusterableModel

from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    PageQuerySet,
    WorkflowMixin,
    Orderable,
)
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.search import index

from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface

import logging

logger = logging.getLogger(__name__)


@register_snippet
class QuickAccessTile(
    ModerationMixin,
    WorkflowMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
    """
    Represents a single Quick Access Tile with a title, description, and icon.
    """

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="icons/")

    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="quickaccesstile"
    )

    objects = PageQuerySet.as_manager()

    content_panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("icon"),
    ]

    panels = content_panels + [PublishingPanel()]

    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.AutocompleteField("title"),
        index.SearchField("description", partial_match=True),
        index.AutocompleteField("description"),
    ]

    def __str__(self):
        """
        Returns the title for a user-friendly representation in the admin.
        """
        return self.title

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Quick Access Tile"
        verbose_name_plural = "Quick Access Tiles"


@register_snippet
class QuickAccessTileCollection(
    ModerationMixin, WorkflowMixin, DraftStateMixin, RevisionMixin, ClusterableModel
):
    """
    A snippet that groups multiple Quick Access Tiles together in a specific order.
    Inherits from ClusterableModel to enable the parent-child relationship for InlinePanel.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of this collection (e.g., 'Homepage Tiles', 'Helpful Links')",
    )

    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="quickaccesstilecollection"
    )
    objects = PageQuerySet.as_manager()

    content_panels = [
        FieldPanel("name"),
        # InlinePanel("quick", label="Quick Access Tiles"),
    ]

    panels = content_panels + [PublishingPanel()]

    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    def __str__(self):
        return self.name

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Quick Access Tile Collection"
        verbose_name_plural = "Quick Access Tile Collections"


class QuickAccessTileOrderable(Orderable):
    """
    This is the "through" model that allows tiles to be ordered within a collection.
    It links QuickAccessTileCollection (parent) to QuickAccessTile (child).
    """
