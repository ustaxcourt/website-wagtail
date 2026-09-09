from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.blocks import RawHTMLBlock
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.common import custom_promote_panels

from home.models.pages.enhanced_standard import (
    EnhancedStandardPage,
    FAQ_FILTER_TAG_CHOICES,
)


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
                            (
                                "filtertag",
                                blocks.ChoiceBlock(
                                    choices=FAQ_FILTER_TAG_CHOICES,
                                    required=True,
                                    label="FilterTag",
                                ),
                            ),
                        ]
                    ),
                    label="Question and Answer",
                    help_text="Add a question and answer. Link the anchor tag number. Select the FAQ FilterTag type in the dropdown.",
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

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels,
        promote_panels=custom_promote_panels,
    )

    class Meta:
        verbose_name = "Enhanced Raw HTML Page"
