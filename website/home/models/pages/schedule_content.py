from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

from wagtail.admin.panels import PublishingPanel
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.fields import StreamField
from wagtail import blocks


class ScheduledPage(Page):
    template = "home/enhanced_standard_page.html"

    class Meta:
        abstract = False

    body = StreamField(
        [
            ("rich_text", blocks.RichTextBlock()),
            ("snippet", SnippetChooserBlock("home.CommonText")),
        ],
        blank=True,
        use_json_field=True,
        help_text="Insert text or choose a snippet.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        PublishingPanel(),
    ]
