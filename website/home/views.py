from wagtail.admin.views.reports import ReportView
import django_filters
from .models import NewsItem
from wagtail.admin.filters import (
    DateRangePickerWidget,
    WagtailFilterSet,
)
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column
from django.utils.html import format_html
from django.conf import settings


class NewsItemReportFilterSet(WagtailFilterSet):
    created_at = django_filters.DateFromToRangeFilter(
        label=_("Created at"), widget=DateRangePickerWidget
    )

    class Meta:
        model = NewsItem
        fields = ["created_at", "banner_options"]


class NewsItemReportView(ReportView):
    title = "News Item Workflow Report"

    index_url_name = "newsitem_report"
    index_results_url_name = "newsitem_report_results"

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
            # accessor=lambda obj: obj.document.url if obj.document else "-"
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

    def get_queryset(self):
        return NewsItem.objects.all()

    def document_url(self, obj):
        # For CSV export - just the URL
        return settings.WAGTAILADMIN_BASE_URL + obj.url if obj else "-"
