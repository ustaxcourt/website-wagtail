from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin, PageQuerySet, WorkflowMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel
from wagtail.snippets.models import register_snippet
from wagtail.search import index


@register_snippet
class NewsItem(
    WorkflowMixin, DraftStateMixin, RevisionMixin, index.Indexed, models.Model
):
    title = models.CharField(
        max_length=255, help_text="Title of the news article", blank=False
    )
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    description = RichTextField(
        blank=False, help_text="Description of the news article"
    )

    publish_date = models.DateTimeField(
        help_text="News article publish date", blank=False
    )

    homepage_display_expiration_date = models.DateTimeField(
        help_text="Date after which the news article will no longer be displayed on the homepage",
        blank=True,
        null=True,
    )

    BANNER_CHOICES = [
        ("none", "No banner"),
        ("high", "High priority (Yellow banner)"),
        ("critical", "Critical (Red banner)"),
    ]

    banner_options = models.CharField(
        max_length=20,
        choices=BANNER_CHOICES,
        default="none",
        help_text="Select the banner type for the news article",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )

    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="newsarticle"
    )

    objects = PageQuerySet.as_manager()

    panels = [
        FieldPanel("title"),
        FieldPanel("document"),
        FieldPanel("image"),
        FieldPanel("description"),
        FieldPanel("publish_date"),
        FieldPanel("homepage_display_expiration_date"),
        FieldPanel("banner_options"),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.AutocompleteField("title"),
        index.SearchField("description", partial_match=True),
        index.AutocompleteField("description"),
    ]

    def save(self, *args, **kwargs):
        if not self.homepage_display_expiration_date and self.publish_date:
            self.homepage_display_expiration_date = self.publish_date + timedelta(
                days=7
            )
        self.created_by = get_user_model().objects.first()
        self.updated_by = self.created_by
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def revisions(self):
        return self._revisions
