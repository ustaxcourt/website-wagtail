from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    WorkflowMixin,
    PreviewableMixin,
)
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.search import index
from wagtail.admin.filters import WagtailFilterSet
import django_filters
from django.forms import DateInput
from django.utils import timezone
from datetime import datetime, time
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface


class NewsItemQuerySet(models.QuerySet):
    def live(self):
        """
        Returns items that are 'live', have a go_live_at
        date in the past, and have not expired.
        """
        now = timezone.now()
        return self.filter(live=True, go_live_at__lte=now).filter(
            # Also check that it hasn't expired
            models.Q(expire_at__isnull=True) | models.Q(expire_at__gt=now)
        )


class NewsItem(
    ModerationMixin,
    WorkflowMixin,
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    index.Indexed,
    models.Model,
):
    objects = NewsItemQuerySet.as_manager()

    BANNER_CHOICES = [
        ("news", "News Item"),
        ("high", "High priority Announcement"),
        ("critical", "Critical Anouncement"),
    ]

    category = models.CharField(max_length=20, choices=BANNER_CHOICES, default="news")

    title = models.CharField(
        max_length=500, help_text="Title of the news article", blank=False
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
    banner = models.ForeignKey(
        "home.Banner",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_items",
    )

    description = RichTextField(
        blank=True, help_text="Summary of the news article", verbose_name="Summary"
    )

    publish_date = models.DateTimeField(
        help_text="News article publish date", blank=False
    )

    homepage_display_expiration_date = models.DateTimeField(
        help_text="Date after which the news article will no longer be displayed on the homepage",
        blank=True,
        null=True,
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

    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="newsitem")

    panels = [
        FieldPanel("category"),
        FieldPanel("title"),
        FieldPanel("document"),
        FieldPanel("image"),
        FieldPanel("description"),
        FieldPanel("banner"),
        FieldPanel("publish_date", classname="publish-date-picker"),
        FieldPanel(
            "homepage_display_expiration_date", classname="expiration-date-picker"
        ),
        PublishingPanel(),
    ]
    edit_handler = ModerationTabbedInterface.create_for_snippet(panels)

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.AutocompleteField("title"),
        index.SearchField("description", partial_match=True),
        index.AutocompleteField("description"),
    ]

    def save(self, *args, **kwargs):
        self.created_by = get_user_model().objects.first()
        self.updated_by = self.created_by
        self.go_live_at = self.publish_date
        super().save(*args, **kwargs)

    def get_preview_template(self, request, mode_name):
        return "previews/news_cards_preview.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["preview_news_items"] = [self]
        return context

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def revisions(self):
        return self._revisions

    @property
    def status(self):
        return self.status_string

    @property
    def document_url(self):
        if self.document and self.document.url:
            return f"{self.document.url}"
        return "-"

    status.fget.short_description = "Status"


class NewsItemFilterSet(WagtailFilterSet):
    status = django_filters.ChoiceFilter(
        field_name="live",
        choices=[
            (True, "Live"),
            (False, "Draft"),
        ],
        label="Status",
    )

    publish_date_from = django_filters.DateFilter(
        field_name="publish_date",
        lookup_expr="gte",
        label="Publish Date From",
        widget=DateInput(attrs={"type": "date"}),
        method="filter_publish_date_from",
    )

    publish_date_to = django_filters.DateFilter(
        field_name="publish_date",
        lookup_expr="lte",
        label="Publish Date To",
        widget=DateInput(attrs={"type": "date"}),
        method="filter_publish_date_to",
    )

    def filter_publish_date_from(self, queryset, name, value):
        if value:
            # Convert date to timezone-aware datetime at start of day
            start_datetime = timezone.make_aware(datetime.combine(value, time.min))
            return queryset.filter(publish_date__gte=start_datetime)
        return queryset

    def filter_publish_date_to(self, queryset, name, value):
        if value:
            # Convert date to timezone-aware datetime at end of day
            end_datetime = timezone.make_aware(datetime.combine(value, time.max))
            return queryset.filter(publish_date__lte=end_datetime)
        return queryset

    class Meta:
        model = NewsItem
        fields = [
            "category",
            "status",
            "publish_date_from",
            "publish_date_to",
        ]


class NewsItemViewSet(SnippetViewSet):
    model = NewsItem
    list_display = [
        "title",
        "document",
        "status",
        "category",
        "publish_date",
        "created_at",
    ]
    filterset_class = NewsItemFilterSet


register_snippet(NewsItem, viewset=NewsItemViewSet)
