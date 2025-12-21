from django.db import models
from django.forms import ValidationError
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin, PageQuerySet, WorkflowMixin
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.snippets.models import register_snippet
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.filters import WagtailFilterSet


class Banner(
    ModerationMixin, WorkflowMixin, DraftStateMixin, RevisionMixin, models.Model
):
    BANNER_CHOICES = [
        ("high", "High priority (Yellow banner)"),
        ("critical", "Critical (Red banner)"),
    ]

    banner_title = models.CharField(
        max_length=115,
        help_text="Character Limit 0f 115",
        blank=False,
    )

    description = RichTextField(blank=False)

    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    priority_level = models.CharField(
        max_length=20,
        choices=BANNER_CHOICES,
        default="none",
        help_text="Select the banner type for the news article",
    )

    banner_start_date = models.DateTimeField(
        help_text="Date/time when the banner should start appearing (required for high and critical priority banner)",
        blank=True,
        null=True,
    )

    banner_end_date = models.DateTimeField(
        help_text="Date/time when the banner should stop appearing (optional - leave blank for indefinite display until replaced by a new banner)",
        blank=True,
        null=True,
    )

    _revisions = GenericRelation("wagtailcore.Revision", related_query_name="banner")
    objects = PageQuerySet.as_manager()

    content_panels = [
        FieldPanel("banner_title"),
        FieldPanel("description"),
        FieldPanel("document"),
        FieldPanel("priority_level"),
        FieldPanel("banner_start_date", classname="banner-start-date-picker"),
        FieldPanel("banner_end_date", classname="banner-end-date-picker"),
    ]
    panels = content_panels + [PublishingPanel()]

    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    def clean(self):
        """
        Validate that high priority banners don't overlap with other high priority banners,
        and critical priority banners don't overlap with other critical priority banners.
        Start date is required for high and critical banners. End date is optional.
        """
        super().clean()

        if not self.title:
            raise ValidationError({"banner_title": "Banner title is required."})

        if not self.description:
            raise ValidationError({"description": "Description is required."})

        # Require start date for high and critical priority banners
        if self.priority_level in ["high", "critical"] and not self.banner_start_date:
            raise ValidationError(
                {
                    "banner_start_date": ValidationError(
                        f"Start date and time are required for {self.priority_level} priority banners.",
                        code="required_start_date",
                    )
                }
            )

        # Only validate if this is a high priority banner with start date set
        if self.priority_level == "high" and self.banner_start_date:
            # Check for overlapping high priority banners
            other_banners = (
                Banner.objects.filter(priority_level="high", live=True)
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
                                    f'Conflicting banner: "{other.banner_title}" '
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
                                        f'Conflicting banner: "{other.banner_title}" '
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
                                        f'Conflicting banner: "{other.banner_title}" '
                                        f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to "
                                        f"{other.banner_end_date.strftime('%Y-%m-%d %H:%M')}). "
                                        f"Please choose a different time period or edit the conflicting banner.",
                                        code="banner_conflict",
                                    )
                                }
                            )

        # Only validate if this is a critical priority banner with start date set
        if self.priority_level == "critical" and self.banner_start_date:
            # Check for overlapping critical priority banners
            other_banners = (
                Banner.objects.filter(priority_level="critical", live=True)
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
                                    f'Conflicting banner: "{other.banner_title}" '
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
                                        f'Conflicting banner: "{other.banner_title}" '
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
                                        f'Conflicting banner: "{other.banner_title}" '
                                        f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to "
                                        f"{other.banner_end_date.strftime('%Y-%m-%d %H:%M')}). "
                                        f"Please choose a different time period or edit the conflicting banner.",
                                        code="banner_conflict",
                                    )
                                }
                            )

    def __str__(self):
        return self.banner_title

    @property
    def revisions(self):
        return self._revisions

    @property
    def category(self):
        if self.priority_level == "high":
            return "High Priority"
        elif self.priority_level == "critical":
            return "Critical"
        return "None"

    @property
    def title(self):
        return self.banner_title

    @property
    def publish_date(self):
        return self.banner_start_date

    @property
    def homepage_display_expiration_date(self):
        return self.banner_end_date

    @property
    def document_url(self):
        if self.document and self.document.url:
            return f"{self.document.url}"
        return "-"


class BannersFilterSet(WagtailFilterSet):
    class Meta:
        model = Banner
        fields = [
            "priority_level",
            "banner_start_date",
            "banner_end_date",
        ]


class BannerViewSet(SnippetViewSet):
    model = Banner
    filterset_class = BannersFilterSet
    list_display = [
        "banner_title",
        "document",
        "priority_level",
        "banner_start_date",
        "banner_end_date",
    ]


register_snippet(Banner, viewset=BannerViewSet)
