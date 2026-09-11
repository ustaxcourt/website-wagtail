import json

from django.db import models
from django.forms import ValidationError
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    WorkflowMixin,
    PreviewableMixin,
)
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.snippets.models import register_snippet
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.filters import WagtailFilterSet


class BannerQuerySet(models.QuerySet):
    def live(self):
        """
        Returns items that are 'live', have a go_live_at
        date in the past, and have not expired.
        """
        now = timezone.now()
        return self.filter(live=True, banner_start_date__lte=now).filter(
            # Also check that it hasn't expired
            models.Q(expire_at__isnull=True) | models.Q(expire_at__gt=now)
        )


class Banner(
    ModerationMixin,
    WorkflowMixin,
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    models.Model,
):
    BANNER_CHOICES = [
        ("high", "High priority (Yellow banner)"),
        ("critical", "Critical (Red banner)"),
    ]

    banner_title = models.CharField(
        max_length=115,
        help_text="Character Limit of 115",
        blank=False,
    )

    description = models.CharField(
        blank=False,
    )

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
    objects = BannerQuerySet.as_manager()

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

    def _check_banner_overlap(self, priority_level):
        """
        Helper method to check for overlapping banners of the same priority level.
        Raises ValidationError if an overlap is detected.
        """
        other_banners = (
            Banner.objects.filter(priority_level=priority_level, live=True)
            .exclude(id=self.id)
            .filter(banner_start_date__isnull=False)
        )

        for other in other_banners:
            has_overlap = False

            # Case 1: Other banner has no end date (indefinite)
            if other.banner_end_date is None:
                if (
                    self.banner_end_date is None
                    or other.banner_start_date < self.banner_end_date
                ):
                    has_overlap = True
            # Case 2: Other banner has an end date
            else:
                if self.banner_end_date is None:
                    # This banner is indefinite
                    has_overlap = other.banner_end_date > self.banner_start_date
                else:
                    # Both have end dates - standard overlap check
                    has_overlap = (
                        self.banner_start_date < other.banner_end_date
                        and self.banner_end_date > other.banner_start_date
                    )

            if has_overlap:
                other_end_text = (
                    "indefinite"
                    if other.banner_end_date is None
                    else other.banner_end_date.strftime("%Y-%m-%d %H:%M")
                )
                raise ValidationError(
                    {
                        "banner_start_date": ValidationError(
                            f"A {priority_level} priority banner is already scheduled during this time period. "
                            f'Conflicting banner: "{other.banner_title}" '
                            f"({other.banner_start_date.strftime('%Y-%m-%d %H:%M')} to {other_end_text}). "
                            f"Please choose a different time period or edit the conflicting banner.",
                            code="banner_conflict",
                        )
                    }
                )

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

        # Check for overlaps if this is a prioritized banner with a start date
        if self.priority_level in ["high", "critical"] and self.banner_start_date:
            self._check_banner_overlap(self.priority_level)

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

    def as_press_release_entry(self, force_release_date=None):
        """
        Build the same dict shape used by PressReleasePage.group_press_releases_by_year
        for standalone banners. Shared here so the News & Announcements listing and the
        announcements-page preview always render identically from a single source of
        truth.

        `force_release_date` lets the preview place this banner into a specific
        year bucket even when it has no banner_start_date yet (or when the
        editor wants to see it regardless of its actual scheduled date).
        """
        banner_label = "High Priority" if self.priority_level == "high" else "Critical"
        release_date = force_release_date
        if release_date is None and self.banner_start_date:
            release_date = self.banner_start_date.date()
        return {
            "is_news_item": True,
            "is_banner": True,
            "release_date": release_date,
            "banner_label": banner_label,
            "banner_title": self.banner_title,
            "banner_body": self.description,
            "banner_type": self.priority_level,
            "details": {
                "description": "",
                "file": self.document,
            },
        }

    # --- Preview support -------------------------------------------------
    # A Banner is rendered in multiple, visually distinct contexts across the
    # site: a dismissible alert at the top of the page, and a historical
    # entry on the News & Announcements page - which itself also shows
    # unrelated NewsItems and other banners at the same time. Rather than a
    # dropdown of separate preview modes, a single preview renders the real
    # PressReleasePage template/context (reusing production code) with this
    # banner forced into view at the top of the page *and* in the listing,
    # regardless of its live status or scheduled dates, so editors see both
    # contexts together alongside real site content in one preview.
    @property
    def preview_modes(self):
        return [("announcements_page", "News & Announcements page")]

    def get_preview_template(self, request, mode_name):
        page = self._get_preview_announcements_page()
        if page is not None:
            return page.get_template(request)
        return "previews/banner_announcements_page_unavailable.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["banner"] = self
        page = self._get_preview_announcements_page()
        if page is not None:
            context.update(page.get_context(request, preview_banner=self))
        context.update(self._forced_top_of_page_banner_context())
        return context

    @staticmethod
    def _get_preview_announcements_page():
        """
        Find a real, live PressReleasePage to render for the "announcements
        page" preview mode. Local import avoids a circular import, since
        press_release.py imports Banner from this module.
        """
        from home.models.pages.press_release import PressReleasePage

        return PressReleasePage.objects.live().first()

    def _forced_top_of_page_banner_context(self):
        """
        base.html always includes yellow_news_banner.html / red_news_banner.html,
        which render whichever banner app.context_processors.yellow_priority_news /
        critical_priority_news supplied (only genuinely live banners within their
        scheduled dates), then further filter client-side by date in JavaScript.

        That means an unpublished/expired/future-scheduled banner - exactly the
        kind of banner an editor is likely previewing - would silently be absent
        from the top of the announcements-page preview, even though its listing
        entry appears further down. To fix that, we override the JSON payload
        for this banner's own priority level so it is always the one shown,
        with no start/end dates, so the client-side date filter always treats
        it as active regardless of its real scheduling.

        These keys are only overridden on the Banner preview response itself;
        real page requests are untouched.
        """
        if self.priority_level not in ("high", "critical"):
            return {}

        payload = json.dumps(
            [
                {
                    "id": self.pk or 0,
                    "title": self.banner_title,
                    "description": str(self.description),
                    "priority_level": self.priority_level,
                    "document_url": self.document.url if self.document else None,
                    # Intentionally omitted (None) so the client-side date
                    # filter always treats this preview banner as active,
                    # regardless of its real banner_start_date/banner_end_date.
                    "banner_start_date": None,
                    "banner_end_date": None,
                }
            ]
        )
        if self.priority_level == "high":
            return {"yellow_priority_news_json": payload, "has_yellow_news": True}
        return {"critical_priority_news_json": payload, "has_critical_news": True}


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
