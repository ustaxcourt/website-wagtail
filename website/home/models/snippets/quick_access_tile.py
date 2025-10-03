from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel, PublishingPanel
from modelcluster.models import ClusterableModel
from wagtail.models import DraftStateMixin, RevisionMixin, PageQuerySet, WorkflowMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.search import index
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface


import logging

logger = logging.getLogger(__name__)

AUTO_MANAGED_COLLECTIONS = []
RESTRICTED_ROLES = []


@register_snippet
class QuickAccessTile(
    ModerationMixin,
    WorkflowMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
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

    # class Meta:
    #     ordering = ["last_name"]

    def save(self, *args, **kwargs):
        logger.info(f"Saving quick access tile: {self}")
        # self.last_updated_date = timezone.now()

        super().save(*args, **kwargs)

        # current_target_collection_name = self.title + "s"

        # collections_to_update = set()

    @property
    def revisions(self):
        return self._revisions

    # def __str__(self):
    #     return self.display_name


# class QuickAccessTileOrderable(Orderable):
#     collection = ParentalKey(
#         "JudgeCollection", related_name="ordered_judges", on_delete=models.CASCADE
#     )
#     judge = models.ForeignKey(
#         "JudgeProfile",
#         on_delete=models.CASCADE,
#         related_name="collection_orderables",  # Changed related_name
#     )

#     panels = [
#         FieldPanel("judge"),
#     ]

#     class Meta(Orderable.Meta):  # Ensure Meta from Orderable is inherited
#         pass


@register_snippet
class QuickAccessTileCollection(
    ModerationMixin, WorkflowMixin, DraftStateMixin, RevisionMixin, ClusterableModel
):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of this collection (e.g., 'Featured Judges', 'Tax Court Judges')",
    )
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="quickaccesstilecollection"
    )
    objects = PageQuerySet.as_manager()

    content_panels = [
        FieldPanel("name"),
        InlinePanel("ordered_quickaccesstile", label="Quick Access Tiles"),
    ]
    panels = content_panels + [PublishingPanel()]

    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def revisions(self):
        return self._revisions
