from django.db import models
from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageBlock
from wagtail.search import index

from home.models.config import IconCategories
from home.models.custom_blocks.button import ButtonBlock
from home.models.custom_blocks.common import link_obj
from home.models.custom_blocks.photo_dedication import PhotoDedicationBlock
from home.models.custom_blocks.common import ColumnBlock
from home.models.snippets.navigation import NavigationRibbon
from home.models.custom_blocks.nested_list import create_nested_list_block
from home.models.custom_blocks.common import custom_promote_panels

table_value_types = [
    ("text", blocks.RichTextBlock()),
]


class IndentStyle(models.TextChoices):
    INDENTED = "indented"
    UNINDENTED = "unindented"


class EnhancedStandardPage(Page):
    class Meta:
        verbose_name = "Enhanced Standard Page"

    navigation_ribbon = models.ForeignKey(
        NavigationRibbon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    body = StreamField(
        [
            (
                "heading",
                blocks.StructBlock(
                    [
                        ("text", blocks.CharBlock()),
                        (
                            "level",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("h2", "Heading 2"),
                                    ("h3", "Heading 3"),
                                    ("h4", "Heading 4"),
                                    ("h5", "Heading 5"),
                                ]
                            ),
                        ),
                        (
                            "id",
                            blocks.CharBlock(
                                required=False,
                                help_text="Optional ID for linking to this heading",
                            ),
                        ),
                    ]
                ),
            ),
            ("h2", blocks.CharBlock(label="Heading 2")),
            ("h3", blocks.CharBlock(label="Heading 3")),
            ("h4", blocks.CharBlock(label="Heading 4")),
            ("paragraph", blocks.RichTextBlock()),
            ("snippet", SnippetChooserBlock("home.CommonText")),
            ("button", ButtonBlock()),
            (
                "hr",
                blocks.BooleanBlock(
                    label="Horizontal Rule",
                    default=True,
                    help_text="Add 'Horizontal Rule'.",
                ),
            ),
            (
                "iframe",
                blocks.StructBlock(
                    [
                        ("src", blocks.URLBlock(required=True)),
                        ("width", blocks.CharBlock(required=True)),
                        ("height", blocks.CharBlock(required=True)),
                        ("class", blocks.CharBlock(required=False)),
                        ("loading", blocks.CharBlock(required=False)),
                        ("data_delay", blocks.CharBlock(required=False)),
                        ("name", blocks.CharBlock(required=False)),
                        ("title", blocks.CharBlock(required=False)),
                    ]
                ),
            ),
            (
                "alert",
                blocks.StructBlock(
                    [
                        (
                            "alert_type",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("info", "Info"),
                                    ("success", "Success"),
                                ],
                                default="info",
                            ),
                        ),
                        ("content", blocks.RichTextBlock()),
                    ],
                ),
            ),
            ("image", ImageBlock()),
            ("photo_dedication", PhotoDedicationBlock()),
            (
                "table",
                TypedTableBlock(
                    table_value_types,
                ),
            ),
            (
                "unstyled_table",
                TypedTableBlock(table_value_types),
            ),
            ("list", create_nested_list_block(max_depth=4)),
            (
                "links",
                blocks.StructBlock(
                    [
                        (
                            "class",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("indented", IndentStyle.INDENTED),
                                    ("unindented", IndentStyle.UNINDENTED),
                                ],
                                default=IndentStyle.INDENTED,
                            ),
                        ),
                        ("links", link_obj),
                    ]
                ),
            ),
            (
                "questionanswers",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("question", blocks.CharBlock(required=False)),
                            ("answer", blocks.RichTextBlock()),
                            ("anchortag", blocks.CharBlock()),
                        ]
                    ),
                    label="Question and Answer",
                    help_text="Add a question and answer with anchor tag for linking",
                ),
            ),
            ("columns", ColumnBlock()),
            (
                "embedded_video",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(required=False)),
                        ("description", blocks.RichTextBlock(required=False)),
                        ("video_url", blocks.URLBlock(required=False)),
                    ]
                ),
            ),
            (
                "card",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            (
                                "icon",
                                blocks.ChoiceBlock(
                                    choices=[
                                        (
                                            icon.value,
                                            icon.name.replace("_", " ").title(),
                                        )
                                        for icon in IconCategories
                                    ],
                                    required=True,
                                ),
                            ),
                            ("title", blocks.CharBlock(required=True)),
                            ("description", blocks.RichTextBlock(required=True)),
                            (
                                "color",
                                blocks.ChoiceBlock(
                                    choices=[
                                        ("green", "Green"),
                                        ("yellow", "Yellow"),
                                    ],
                                    required=True,
                                ),
                            ),
                        ],
                        label="Card",
                    ),
                    label="Card Set",
                ),
            ),
        ],
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("navigation_ribbon"),
        FieldPanel("body"),
    ]

    promote_panels = custom_promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
