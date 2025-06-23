from wagtail.admin.panels import PublishingPanel

from home.models.pages.enhanced_standard import EnhancedStandardPage


class ScheduledPage(EnhancedStandardPage):
    template = "home/enhanced_standard_page.html"

    class Meta:
        abstract = False

    content_panels = EnhancedStandardPage.content_panels + [
        PublishingPanel(),
    ]
