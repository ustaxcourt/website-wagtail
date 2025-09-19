from wagtail.admin.views.reports import ReportView

from .models import NewsItem


class NewsItemReportView(ReportView):
    # includes string representation as a single column only

    def get_queryset(self):
        return NewsItem.objects.all()
