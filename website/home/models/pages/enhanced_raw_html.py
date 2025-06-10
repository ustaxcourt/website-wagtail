from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.blocks import RawHTMLBlock
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from home.models.pages.enhanced_standard import EnhancedStandardPage


class EnhancedRawHTMLPage(EnhancedStandardPage):
    """
    A specialized page type that allows embedding raw HTML.
    """

    template = "home/enhanced_standard_page.html"

    raw_html_body = StreamField(
        [
            ("raw_html", RawHTMLBlock(label="Raw HTML")),
            (
                "questionanswers",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("question", blocks.CharBlock(required=False)),
                            (
                                "answer",
                                blocks.StructBlock(
                                    [
                                        (
                                            "rich_text",
                                            blocks.RichTextBlock(required=False),
                                        ),
                                        (
                                            "html_block",
                                            blocks.RawHTMLBlock(required=False),
                                        ),
                                    ],
                                    required=False,
                                ),
                            ),
                            ("anchortag", blocks.CharBlock(required=False)),
                        ]
                    ),
                    label="Question and Answer",
                    help_text="Add a question and answer with anchor tag for linking",
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("raw_html_body"),
    ]

    search_fields = EnhancedStandardPage.search_fields + [
        index.SearchField("raw_html_body"),
    ]

    class Meta:
        verbose_name = "Enhanced Raw HTML Page"
