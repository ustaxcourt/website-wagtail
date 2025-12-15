from wagtail.admin.views.reports import ReportView
from wagtail.documents.views.chooser import DocumentChooserViewSet
import django_filters
from .models import NewsItem, Banner
from wagtail.admin.filters import (
    WagtailFilterSet,
)
from wagtail.admin.ui.tables import Column
from django.utils.html import format_html
from django.utils import timezone


class NewsItemReportFilterSet(WagtailFilterSet):
    category = django_filters.ChoiceFilter(
        label="Category",
        choices=[
            ("news", "News Item"),
            ("high", "High Priority Announcement"),
            ("critical", "Critical Announcement"),
        ],
        empty_label="All Categories",
    )

    # publish_date_range = DateFromToRangeFilter(
    #     field_name="publish_date",
    #     label="Publish Date Range",
    #     widget=DateRangePickerWidget,
    # )

    # homepage_display_expiration_date_range = DateFromToRangeFilter(
    #     field_name="homepage_display_expiration_date",
    #     label="Homepage Display Expiration Date Range",
    #     widget=DateRangePickerWidget,
    # )

    class Meta:
        model = NewsItem
        fields = [
            "category",
            # "title",
            # "created_at",
            # "publish_date_range",
            # "homepage_display_expiration_date_range",
        ]


class NewsItemReportView(ReportView):
    title = "News & Announcements Report"

    index_url_name = "news_and_announcements_report"
    index_results_url_name = "news_and_announcements_report_results"

    # Disable filtering since we're combining two different model types
    filterset_class = NewsItemReportFilterSet

    columns = [
        Column(
            "category",
            label="Category",
            accessor=lambda obj: format_html(
                "<div style='font-weight: bold;'>{}</div>",
                format_category(obj),
            ),
        ),
        Column(
            "title",
            label="Title",
            accessor=lambda obj: format_html(
                '<div style="font-weight: bold;">{}</div>',
                get_title(obj),
            ),
        ),
        Column(
            "document",
            label="Document",
            accessor=lambda obj: format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.document.url,
                obj.document.filename,
            )
            if obj.document
            else "-",
        ),
        Column(
            "publish_date",
            label="Publish Date",
            accessor=lambda obj: get_publish_date(obj),
        ),
        Column(
            "homepage_display_expiration_date",
            label="Homepage Expiration",
            accessor=lambda obj: get_homepage_expiration(obj),
        ),
        Column(
            "created_at", label="Created At", accessor=lambda obj: get_created_at(obj)
        ),
    ]

    list_export = [
        "id",
        "category",
        "title",
        "publish_date",
        "homepage_display_expiration_date",
        "document_url",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.custom_field_preprocess = self.custom_field_preprocess.copy()
        self.custom_field_preprocess["publish_date"] = {
            self.FORMAT_CSV: to_default_tz,
            self.FORMAT_XLSX: to_default_tz,
        }
        self.custom_field_preprocess["homepage_display_expiration_date"] = {
            self.FORMAT_CSV: to_default_tz,
            self.FORMAT_XLSX: to_default_tz,
        }

    def get_queryset(self):
        # Get all news items
        news_items = list(NewsItem.objects.all())

        # Get banner IDs that are already referenced by news items
        # We don't want to show these banners separately since they're already
        # represented by their associated news item
        # banner_ids_in_news_items = set(
        #     NewsItem.objects.filter(banner__isnull=False).values_list(
        #         "banner_id", flat=True
        #     )
        # )

        # Get all banners that are NOT referenced by news items
        # These are standalone banners that should appear as separate entries
        banners = list(Banner.objects.all())
        # .exclude(id__in=banner_ids_in_news_items)

        # Mark each object with its type for easier handling
        for item in news_items:
            item._is_banner = False
        for banner in banners:
            banner._is_banner = True

        # Combine and sort by created_at (most recent first)
        combined = news_items + banners
        combined.sort(key=lambda x: get_created_at(x) or timezone.now(), reverse=True)

        return combined

    def get_filtered_queryset(self, queryset=None, filters=None):
        """Apply filters to the combined queryset"""
        queryset = queryset or self.get_queryset()
        filters = filters or self.get_filterset_kwargs().get("data", {})

        print("Filters applied:", filters)

        if not filters:
            return queryset

        filtered = queryset

        # Filter by category
        category = filters.get("category")
        if category:
            filtered = [
                obj for obj in filtered if self._get_obj_category(obj) == category
            ]

        return filtered

    def _get_obj_category(self, obj):
        """Get category value for an object for filtering purposes"""
        if getattr(obj, "_is_banner", False):
            return obj.priority_level
        return getattr(obj, "category", None)


def get_title(obj):
    """Get title based on object type"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        priority = (
            "High priority banner"
            if obj.priority_level == "high"
            else "Critical banner"
        )
        return f"{priority}: {obj.banner_title}"
    return obj.title if hasattr(obj, "title") and obj.title else "-"


def get_publish_date(obj):
    """Get publish date based on object type"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        return obj.banner_start_date if obj.banner_start_date else "-"
    return (
        obj.publish_date if hasattr(obj, "publish_date") and obj.publish_date else "-"
    )


def get_homepage_expiration(obj):
    """Get homepage expiration based on object type"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        return obj.banner_end_date if obj.banner_end_date else "-"
    return (
        obj.homepage_display_expiration_date
        if hasattr(obj, "homepage_display_expiration_date")
        and obj.homepage_display_expiration_date
        else "-"
    )


def get_created_at(obj):
    """Get created_at based on object type"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        return obj.first_published_at if obj.first_published_at else "-"
    return obj.created_at if hasattr(obj, "created_at") else "-"


def format_category(obj):
    # If this object was tagged as a banner in get_queryset, handle it separately
    if getattr(obj, "_is_banner", False):
        pl = getattr(obj, "priority_level", None)
        if pl == "high":
            return "High Priority Announcement"
        if pl == "critical":
            return "Critical Announcement"
        # fallback for banners with no priority set
        return "Banner"

    # For non-banner objects (e.g. NewsItem), prefer category, fall back to priority_level
    cat = getattr(obj, "category", None)
    if cat:
        if cat == "news":
            return "News Item"
        if cat == "high":
            return "High Priority Announcement"
        if cat == "critical":
            return "Critical Announcement"
        return str(cat).capitalize()

    pl = getattr(obj, "priority_level", None)
    if pl == "critical":
        return "Critical Announcement"
    if pl == "high":
        return "High Priority Announcement"

    return "-"


def to_default_tz(dt):
    current_tz = timezone.get_current_timezone()

    if dt is None:
        return dt
    if timezone.is_aware(dt):
        dt = dt.astimezone(current_tz)
        dt_naive = dt.astimezone().replace(tzinfo=None)
        return dt_naive
    return dt


class SVGChooseView(DocumentChooserViewSet.choose_view_class):
    def get_object_list(self):
        queryset = super().get_object_list()

        return queryset.filter(file__iendswith=".svg")


class SVGChooserViewSet(DocumentChooserViewSet):
    choose_view_class = SVGChooseView


svg_chooser_viewset = SVGChooserViewSet("svg_chooser")
