from wagtail.admin.views.reports import ReportView
from wagtail.documents.views.chooser import DocumentChooserViewSet
import django_filters

from search.models.definitionsQuery import DefinitionsQuery
from home.models.pages.definitions import DefinitionsPage
from .models import NewsItem
from wagtail.admin.filters import (
    DateRangePickerWidget,
    WagtailFilterSet,
)
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column
from django.utils.html import format_html
from django.utils import timezone
from django_filters import DateFromToRangeFilter


class NewsItemReportFilterSet(WagtailFilterSet):
    created_at = django_filters.DateFromToRangeFilter(
        label=_("Created at"), widget=DateRangePickerWidget
    )

    title = django_filters.CharFilter(lookup_expr="icontains", label="Title")

    publish_date_range = DateFromToRangeFilter(
        field_name="publish_date",
        label="Publish Date Range",
        widget=DateRangePickerWidget,
    )

    homepage_display_expiration_date_range = DateFromToRangeFilter(
        field_name="homepage_display_expiration_date",
        label="Homepage Display Expiration Date Range",
        widget=DateRangePickerWidget,
    )

    class Meta:
        model = NewsItem
        fields = [
            "title",
            "created_at",
            "banner_options",
            "publish_date_range",
            "homepage_display_expiration_date_range",
        ]


class NewsItemReportView(ReportView):
    title = "News Item Workflow Report"

    index_url_name = "news_and_announcements_report"
    index_results_url_name = "news_and_announcements_report_results"

    filterset_class = NewsItemReportFilterSet

    columns = [
        Column(
            "title",
            label="Title",
            accessor=lambda obj: format_html(
                '<div style="font-weight: bold;">{}</div>',
                obj.title if obj.title else "-",
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
            accessor=lambda obj: obj.publish_date if obj.publish_date else "-",
        ),
        Column(
            "homepage_display_expiration_date",
            label="Homepage Expiration",
            accessor=lambda obj: obj.homepage_display_expiration_date
            if obj.homepage_display_expiration_date
            else "-",
        ),
        Column(
            "banner_options",
            label="Banner Type",
            accessor=lambda obj: {
                "critical": format_html(
                    '<div style="background-color: red; color: black; white-space: nowrap; padding: 5px;">Critical</div>'
                ),
                "high": format_html(
                    '<div style="background-color: orange; color: black; white-space: nowrap; padding: 5px;">High Priority</div>'
                ),
                "none": "No banner",
            }.get(obj.banner_options),
        ),
        Column("created_at", label="Created At", accessor=lambda obj: obj.created_at),
    ]

    list_export = [
        "id",
        "title",
        "publish_date",
        "homepage_display_expiration_date",
        "banner_options",
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
        return NewsItem.objects.all()


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

    class Meta:
        model = DefinitionsQuery
        fields = [
            "query_string",
        ]


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
            label="In list?",
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


class SVGChooseView(DocumentChooserViewSet.choose_view_class):
    def get_object_list(self):
        queryset = super().get_object_list()

        return queryset.filter(file__iendswith=".svg")


class SVGChooserViewSet(DocumentChooserViewSet):
    choose_view_class = SVGChooseView


svg_chooser_viewset = SVGChooserViewSet("svg_chooser")
