# Vendored from wagtail-external-links-report 0.1.1
# (https://github.com/PBahner/wagtail-external-links-report), whose PyPI
# package pins `wagtail~=7.1` and cannot be installed alongside Wagtail 8.
# The code itself only relies on stable Wagtail admin report APIs, so it is
# vendored here rather than depending on an unmaintained third-party package.
from wagtail.admin.views.reports import PageReportView
from wagtail.models import Page

from home.vendor.wagtail_external_links_report.utils.link_extractor import (
    LinkExtractor,
)


class ExternalLinksReportView(PageReportView):
    results_template_name = (
        "wagtail_external_links_report/external_links_report_results.html"
    )
    page_title = "used links"

    def get_queryset(self):
        pages = Page.objects.live().specific()
        extractor = self.get_extractor()
        return [p for p in pages if extractor.extract_from_page(p)]

    def get_extractor(self):
        return LinkExtractor(
            allowed_fields=["body"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extractor = self.get_extractor()

        for page in context["page_obj"]:
            page.external_links = extractor.extract_from_page(page)

        return context
