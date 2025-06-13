from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

# from wagtail.models import DraftStateMixin, RevisionMixin
from wagtail.admin.panels import PublishingPanel


class ScheduledPage(Page):
    template = "home/standard_page.html"

    class Meta:
        abstract = False

    body = RichTextField(blank=True, help_text="Insert text here.")

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        PublishingPanel(),
    ]
