from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin, WorkflowMixin
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
    index.Indexed,
    models.Model,
):
    objects = NewsItemQuerySet.as_manager()

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

    banner_start_date = models.DateTimeField(
        help_text="Date/time when the banner should start appearing (required for high and critical priority banners)",
        blank=True,
        null=True,
    )

    banner_end_date = models.DateTimeField(
        help_text="Date/time when the banner should stop appearing (optional - leave blank for indefinite display until replaced by a new banner)",
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
        FieldPanel("title"),
        FieldPanel("document"),
        FieldPanel("image"),
        FieldPanel("description"),
        FieldPanel("publish_date", classname="publish-date-picker"),
        FieldPanel(
            "homepage_display_expiration_date", classname="expiration-date-picker"
        ),
        FieldPanel("banner_options"),
        FieldPanel("banner_start_date", classname="banner-start-date-picker"),
        FieldPanel("banner_end_date", classname="banner-end-date-picker"),
        PublishingPanel(),
    ]
    edit_handler = ModerationTabbedInterface.create_for_snippet(panels)

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.AutocompleteField("title"),
        index.SearchField("description", partial_match=True),
        index.AutocompleteField("description"),
    ]

    def clean(self):
        """
        Validate that high priority banners don't overlap with other high priority banners,
        and critical priority banners don't overlap with other critical priority banners.
        Start date is required for high and critical banners. End date is optional.
        """
        super().clean()

        # Require start date for high and critical priority banners
        if self.banner_options in ["high", "critical"] and not self.banner_start_date:
            raise ValidationError(
                {
                    "banner_start_date": ValidationError(
                        f"Start date and time are required for {self.banner_options} priority banners.",
                        code="required_start_date",
                    )
                }
            )

        # Only validate if this is a high priority banner with start date set
        if self.banner_options == "high" and self.banner_start_date:
            # Check for overlapping high priority banners
            other_banners = (
                NewsItem.objects.filter(banner_options="high", live=True)
                .exclude(id=self.id)  # Exclude self when editing
                .filter(banner_start_date__isnull=False)
            )

            for other in other_banners:
                # Check if there's an overlap
                # Case 1: Other banner has no end date (indefinite) - conflicts if it starts before this one ends (or this one is indefinite)
                if other.banner_end_date is None:
                    # If other starts before this ends (or this is indefinite), there's a conflict
                    if (
                        self.banner_end_date is None
                        or other.banner_start_date < self.banner_end_date
                    ):
                        # But only if this starts before other ends (which is never, so always conflicts if we reach here)
                        end_text = "indefinite"
                        raise ValidationError(
                            {
                                "banner_start_date": ValidationError(
                                    f"A high priority banner is already scheduled during this time period. "
                                    f'Conflicting banner: "{other.title}" '
                                    f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to {end_text}). "
                                    f"Please choose a different time period or edit the conflicting banner.",
                                    code="banner_conflict",
                                )
                            }
                        )
                # Case 2: Other banner has an end date
                elif other.banner_end_date:
                    # Standard overlap check: this starts before other ends AND this ends after other starts
                    # If this banner has no end date, it's indefinite, so check if it starts before other ends
                    if self.banner_end_date is None:
                        # This is indefinite, conflicts if other ends after this starts
                        if other.banner_end_date > self.banner_start_date:
                            raise ValidationError(
                                {
                                    "banner_start_date": ValidationError(
                                        f"A high priority banner is already scheduled during this time period. "
                                        f'Conflicting banner: "{other.title}" '
                                        f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to "
                                        f"{other.banner_end_date.strftime('%Y-%m-%d %H:%M')}). "
                                        f"Please choose a different time period or edit the conflicting banner.",
                                        code="banner_conflict",
                                    )
                                }
                            )
                    else:
                        # Both have end dates, standard overlap check
                        if (
                            self.banner_start_date < other.banner_end_date
                            and self.banner_end_date > other.banner_start_date
                        ):
                            raise ValidationError(
                                {
                                    "banner_start_date": ValidationError(
                                        f"A high priority banner is already scheduled during this time period. "
                                        f'Conflicting banner: "{other.title}" '
                                        f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to "
                                        f"{other.banner_end_date.strftime('%Y-%m-%d %H:%M')}). "
                                        f"Please choose a different time period or edit the conflicting banner.",
                                        code="banner_conflict",
                                    )
                                }
                            )

        # Only validate if this is a critical priority banner with start date set
        if self.banner_options == "critical" and self.banner_start_date:
            # Check for overlapping critical priority banners
            other_banners = (
                NewsItem.objects.filter(banner_options="critical", live=True)
                .exclude(id=self.id)  # Exclude self when editing
                .filter(banner_start_date__isnull=False)
            )

            for other in other_banners:
                # Check if there's an overlap
                # Case 1: Other banner has no end date (indefinite) - conflicts if it starts before this one ends (or this one is indefinite)
                if other.banner_end_date is None:
                    # If other starts before this ends (or this is indefinite), there's a conflict
                    if (
                        self.banner_end_date is None
                        or other.banner_start_date < self.banner_end_date
                    ):
                        # But only if this starts before other ends (which is never, so always conflicts if we reach here)
                        end_text = "indefinite"
                        raise ValidationError(
                            {
                                "banner_start_date": ValidationError(
                                    f"A critical priority banner is already scheduled during this time period. "
                                    f'Conflicting banner: "{other.title}" '
                                    f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to {end_text}). "
                                    f"Please choose a different time period or edit the conflicting banner.",
                                    code="banner_conflict",
                                )
                            }
                        )
                # Case 2: Other banner has an end date
                elif other.banner_end_date:
                    # Standard overlap check: this starts before other ends AND this ends after other starts
                    # If this banner has no end date, it's indefinite, so check if it starts before other ends
                    if self.banner_end_date is None:
                        # This is indefinite, conflicts if other ends after this starts
                        if other.banner_end_date > self.banner_start_date:
                            raise ValidationError(
                                {
                                    "banner_start_date": ValidationError(
                                        f"A critical priority banner is already scheduled during this time period. "
                                        f'Conflicting banner: "{other.title}" '
                                        f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to "
                                        f"{other.banner_end_date.strftime('%Y-%m-%d %H:%M')}). "
                                        f"Please choose a different time period or edit the conflicting banner.",
                                        code="banner_conflict",
                                    )
                                }
                            )
                    else:
                        # Both have end dates, standard overlap check
                        if (
                            self.banner_start_date < other.banner_end_date
                            and self.banner_end_date > other.banner_start_date
                        ):
                            raise ValidationError(
                                {
                                    "banner_start_date": ValidationError(
                                        f"A critical priority banner is already scheduled during this time period. "
                                        f'Conflicting banner: "{other.title}" '
                                        f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to "
                                        f"{other.banner_end_date.strftime('%Y-%m-%d %H:%M')}). "
                                        f"Please choose a different time period or edit the conflicting banner.",
                                        code="banner_conflict",
                                    )
                                }
                            )

    def save(self, *args, **kwargs):
        self.created_by = get_user_model().objects.first()
        self.updated_by = self.created_by
        self.go_live_at = self.publish_date
        super().save(*args, **kwargs)

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
        fields = ["banner_options", "status", "publish_date_from", "publish_date_to"]


class NewsItemViewSet(SnippetViewSet):
    model = NewsItem
    list_display = ["title", "document", "status", "publish_date", "created_at"]
    filterset_class = NewsItemFilterSet


register_snippet(NewsItem, viewset=NewsItemViewSet)
