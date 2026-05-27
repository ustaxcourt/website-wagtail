from django.db.models.functions import Lower, Trim
from wagtail.admin.views.reports import ReportView
from wagtail.documents.views.chooser import DocumentChooserViewSet
import django_filters
from datetime import date, datetime

from search.models.definitionsQuery import DefinitionsQuery
from home.models.pages.definitions import DefinitionsPage
from .models import NewsItem, Banner
from wagtail.admin.filters import (
    WagtailFilterSet,
    DateRangePickerWidget,
)
from wagtail.admin.ui.tables import Column
from django.utils.html import format_html
from django.utils import timezone
from wagtail_external_links_report.views import ExternalLinksReportView
from home.utils.custom_link_extractor import CustomLinkExtractor
from wagtail.admin.views.generic.base import BaseListingView


class NewsItemReportFilterSet(WagtailFilterSet):
    publish_date_range = django_filters.DateFromToRangeFilter(
        field_name="publish_date",
        label="Publish Date Range",
        widget=DateRangePickerWidget,
    )

    homepage_display_expiration_date_range = django_filters.DateFromToRangeFilter(
        field_name="homepage_display_expiration_date",
        label="Homepage Display Expiration Date Range",
        widget=DateRangePickerWidget,
    )

    class Meta:
        model = NewsItem
        fields = [
            "title",
            "created_at",
            "publish_date_range",
            "homepage_display_expiration_date_range",
        ]


class NewsItemReportView(ReportView):
    title = "News & Announcements Report"

    index_url_name = "news_and_announcements_report"
    index_results_url_name = "news_and_announcements_report_results"

    # Disable filtering since we're combining two different model types
    filterset_class = NewsItemReportFilterSet

    export_headings = {
        "id": "ID",
        "category": "Category",
        "title": "Title",
        "banner_information": "Banner Information",
        "publish_date": "Publish Date",
        "homepage_display_expiration_date": "Homepage Expiration",
        "document_url": "Document URL",
    }

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
        "banner_information",
        "publish_date",
        "homepage_display_expiration_date",
        "document_url",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Custom preprocessing for datetime fields to convert timezone
        # Note: to_row_dict now handles the extraction of values,
        # so preprocessing receives VALUES, not objects
        self.custom_field_preprocess = self.custom_field_preprocess.copy()
        self.custom_field_preprocess["publish_date"] = {
            self.FORMAT_CSV: lambda value: to_default_tz(value) if value else "",
            self.FORMAT_XLSX: lambda value: to_default_tz(value) if value else "",
        }
        self.custom_field_preprocess["homepage_display_expiration_date"] = {
            self.FORMAT_CSV: lambda value: to_default_tz(value) if value else "",
            self.FORMAT_XLSX: lambda value: to_default_tz(value) if value else "",
        }

    def get_queryset(self):
        # Get all news items
        news_items = list(NewsItem.objects.all())

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

        if not filters:
            return queryset

        filtered = queryset

        title = filters.get("title")
        if title:
            filtered = [
                obj for obj in filtered if title.lower() in get_title(obj).lower()
            ]

        created_at = filters.get("created_at")
        if created_at:
            created_at_date = datetime.strptime(created_at, "%Y-%m-%d").date()
            filtered = [
                obj for obj in filtered if get_created_at(obj).date() == created_at_date
            ]

        # Filter by publish date
        publish_date_from = filters.get("publish_date_range_from")
        publish_date_to = filters.get("publish_date_range_to")
        if publish_date_from or publish_date_to:

            def in_publish_date_range(obj):
                pub_date = get_publish_date_raw(obj)
                if pub_date is None or pub_date == "-":
                    return False
                # Convert datetime to date if needed
                if hasattr(pub_date, "date"):
                    pub_date = pub_date.date()
                if (
                    publish_date_from
                    and pub_date
                    < datetime.strptime(publish_date_from, "%Y-%m-%d").date()
                ):
                    return False
                if (
                    publish_date_to
                    and pub_date > datetime.strptime(publish_date_to, "%Y-%m-%d").date()
                ):
                    return False
                return True

            filtered = [obj for obj in filtered if in_publish_date_range(obj)]

        # Filter by homepage display expiration date
        homepage_date_from = filters.get("homepage_display_expiration_date_range_from")
        homepage_date_to = filters.get("homepage_display_expiration_date_range_to")

        if homepage_date_from or homepage_date_to:

            def in_homepage_date_range(obj):
                exp_date = get_homepage_expiration_raw(obj)
                if exp_date is None or exp_date == "-":
                    return False
                # Convert datetime to date if needed
                if hasattr(exp_date, "date"):
                    exp_date = exp_date.date()
                if (
                    homepage_date_from
                    and exp_date
                    < datetime.strptime(homepage_date_from, "%Y-%m-%d").date()
                ):
                    return False
                if (
                    homepage_date_to
                    and exp_date
                    > datetime.strptime(homepage_date_to, "%Y-%m-%d").date()
                ):
                    return False
                return True

            filtered = [obj for obj in filtered if in_homepage_date_range(obj)]

        return filtered

    def get_heading(self, queryset, field):
        """
        Override get_heading to handle list queryset (instead of QuerySet).
        The parent class tries to access queryset.model which doesn't exist on lists.
        """
        # Check if we have a custom heading defined
        heading_override = self.export_headings.get(field)
        if heading_override:
            return heading_override
        # For list-based queryset, just return the field name capitalized
        return field.replace("_", " ").title()

    def to_row_dict(self, item):
        """
        Override to_row_dict to handle computed fields that don't exist as attributes.
        Maps export field names to their computed values using helper functions.
        """
        from collections import OrderedDict

        row_dict = OrderedDict()
        for field in self.list_export:
            if field == "category":
                row_dict[field] = format_category(item)
            elif field == "title":
                row_dict[field] = get_title(item)
            # elif field == "banner_information":
            #     row_dict[field] = get_banner_information(item)
            elif field == "publish_date":
                row_dict[field] = get_publish_date_raw(item)
            elif field == "homepage_display_expiration_date":
                row_dict[field] = get_homepage_expiration_raw(item)
            elif field == "document_url":
                row_dict[field] = getattr(item, "document_url", "-")
            else:
                # For standard fields like 'id', get the attribute directly
                row_dict[field] = getattr(item, field, None)

        return row_dict

    def get_filename(self):
        """Generate filename for export"""
        today = date.today().strftime("%Y-%m-%d")
        return f"News_and_Announcements_Report_{today}"


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


def get_publish_date_raw(obj):
    """Get raw publish date based on object type (for export)"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        return obj.banner_start_date
    return obj.publish_date if hasattr(obj, "publish_date") else None


def get_publish_date(obj):
    """Get publish date based on object type"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        return obj.banner_start_date if obj.banner_start_date else "-"
    return (
        obj.publish_date if hasattr(obj, "publish_date") and obj.publish_date else "-"
    )


def get_homepage_expiration_raw(obj):
    """Get raw homepage expiration based on object type (for export)"""
    if hasattr(obj, "_is_banner") and obj._is_banner:
        return obj.banner_end_date
    return (
        obj.homepage_display_expiration_date
        if hasattr(obj, "homepage_display_expiration_date")
        else None
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

    # All NewsItems are just "News Item"
    return "News Item"


def to_default_tz(dt):
    current_tz = timezone.get_current_timezone()

    if dt is None:
        return dt
    if timezone.is_aware(dt):
        dt = dt.astimezone(current_tz)
        dt_naive = dt.astimezone().replace(tzinfo=None)
        return dt_naive
    return dt


class SearchDefinitionsReportFilterSet(WagtailFilterSet):
    query_string = django_filters.CharFilter(
        lookup_expr="icontains", label="Search Term"
    )

    number_of_hits = django_filters.RangeFilter(
        field_name="number_of_hits", label="Number of Hits (Range)"
    )

    in_list = django_filters.ChoiceFilter(
        choices=[("yes", "Yes"), ("no", "No")],
        label="In List?",
        method="filter_in_list",  # Tells Django to use the method below
        empty_label="All",
    )

    def filter_in_list(self, queryset, name, value):
        """
        Custom filter to check if the query_string exists in the
        DefinitionsPage word list.
        """
        word_list = [w.lower().strip() for w in DefinitionsPage.getWordList()]

        qs = queryset.annotate(query_list=Lower(Trim("query_string")))

        if value == "yes":
            return qs.filter(query_list__in=word_list)

        elif value == "no":
            return qs.exclude(query_list__in=word_list)

        return queryset

    class Meta:
        model = DefinitionsQuery
        fields = []


class SearchDefinitionsReportView(ReportView):
    title = "Search Definitions Report"

    index_url_name = "search_definitions_report"
    index_results_url_name = "search_definitions_report_results"
    filterset_class = SearchDefinitionsReportFilterSet

    columns = [
        Column(
            "query_string",
            label="Searched Definition",
            accessor=lambda obj: format_html(
                '<div style="font-weight: 600; font-size: 14px;">{}</div>',
                obj.query_string if obj.query_string else "—",
            ),
        ),
        Column(
            "number_of_hits",
            label="Times Searched",
            accessor=lambda obj: format_html(
                '<span style="background-color: #eff6ff; color: #2563eb; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px;">{}</span>',
                obj.number_of_hits,
            )
            if obj.number_of_hits
            else "-",
        ),
        Column(
            "id",
            label="On List?: Yes/No",
            accessor=lambda obj: format_html(
                '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;">{}</span>',
                "#dcfce7"
                if obj.query_string.lower().strip() in DefinitionsPage.getWordList()
                else "#f3f4f6",
                "#166534"
                if obj.query_string.lower().strip() in DefinitionsPage.getWordList()
                else "#4b5563",
                "YES"
                if obj.query_string.lower().strip() in DefinitionsPage.getWordList()
                else "NO",
            ),
        ),
    ]

    list_export = [
        "id",
        "query_string",
        "number_of_hits",
    ]

    def get_queryset(self):
        return DefinitionsQuery.objects.all().order_by("-id")

    def get_filename(self):
        today = date.today().strftime("%Y-%m-%d")
        return f"Search_Terms_Report_{today}"


# ------------------- SVG --------------------


class SVGChooseView(DocumentChooserViewSet.choose_view_class):
    def get_object_list(self):
        queryset = super().get_object_list()

        return queryset.filter(file__iendswith=".svg")


class SVGChooserViewSet(DocumentChooserViewSet):
    choose_view_class = SVGChooseView


SVG_CHOOSER_VIEWSET = SVGChooserViewSet("svg_chooser")
# ------------------- PDF --------------------


class PDFChooseView(DocumentChooserViewSet.choose_view_class):
    def get_object_list(self):
        queryset = super().get_object_list()

        return queryset.filter(file__iendswith=".pdf")


class PDFChooserViewSet(DocumentChooserViewSet):
    choose_view_class = PDFChooseView


PDF_CHOOSER_VIEWSET = PDFChooserViewSet("pdf_chooser")


class CustomExternalLinksReportView(ExternalLinksReportView):
    results_template_name = "home/custom_external_links_report_results.html"
    page_title = "External Links"
    list_export = ["title", "slug", "link_text", "link_url"]
    export_headings = {
        "title": "Source Page Name",
        "slug": "Source Slug",
        "link_text": "Link Label",
        "link_url": "Link Destination",
    }

    def get_extractor(self):
        return CustomLinkExtractor()

    def get_context_data(self, **kwargs):
        context = BaseListingView.get_context_data(self, **kwargs)
        extractor = self.get_extractor()

        for page in context["object_list"]:
            page.external_links = extractor.extract_from_page(page)

        if self.is_export:
            context["object_list"] = self.export_rows(context["object_list"])

        return context

    def export_rows(self, page_list):
        rows = []
        for page in page_list:
            for link in page.external_links:
                rows.append(
                    {
                        "title": page.title,
                        "slug": page.slug,
                        "link_text": link["text"],
                        "link_url": link["url"],
                    }
                )
        return rows
