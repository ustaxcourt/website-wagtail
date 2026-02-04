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
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitForm
from home.blocks import QuickAccessTilesBlock


table_value_types = [
    ("text", blocks.RichTextBlock()),
]


class IndentStyle(models.TextChoices):
    INDENTED = "indented"
    UNINDENTED = "unindented"


class StyledCalloutBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=True, help_text="The title of this special element"
    )
    text = blocks.RichTextBlock(required=True, help_text="The paragraph content")
    callout_type = blocks.ChoiceBlock(
        required=True,
        default="info",
        choices=[
            ("info", "Info"),
            ("warning", "Warning"),
            ("success", "Success"),
            ("error", "Error"),
            ("emergency", "Emergency"),
        ],
    )

    class Meta:
        label = "Callout Block"
        icon = "info-circle"
        template = "callout_block.html"


class AccordianBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255, required=True, help_text="Title user will see before opening"
    )
    description = blocks.StreamBlock(
        [
            ("prose", blocks.RichTextBlock()),
            ("callout", StyledCalloutBlock()),
        ],
        required=True,
        help_text="Add text or special elements to the body",
    )

    class Meta:
        label = "Accordion Block"
        template = "accordian_block.html"


class GridCellBlock(blocks.StructBlock):
    header = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Optional header for this grid cell",
    )
    caption = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Optional caption for this grid cell (links allowed)",
    )
    italic_caption = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Make the caption text italic",
    )
    body = blocks.StreamBlock(
        [
            ("prose", blocks.RichTextBlock()),
            ("callout", StyledCalloutBlock()),
        ],
        required=True,
        help_text="Add text or special elements to the cell body",
    )

    class Meta:
        label = "Grid Cell"
        icon = "placeholder"


class GridBlock(blocks.StructBlock):
    columns = blocks.ChoiceBlock(
        required=True,
        default=2,
        choices=[
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
        ],
        help_text="Max number of columns in the grid (1-4)",
    )
    width = blocks.ChoiceBlock(
        required=True,
        default="full",
        choices=[
            ("full", "Full Width"),
        ],
        help_text="Maximum width of the grid",
    )
    gridStyle = blocks.ChoiceBlock(
        required=True,
        default="styled",
        choices=[
            ("styled", "Styled"),
            ("unstyled", "Unstyled"),
        ],
        help_text="Style of the grid",
    )
    cells = blocks.ListBlock(
        GridCellBlock(),
        help_text="Add cells to the grid. Cells will fill row-by-row based on the number of columns selected.",
    )

    class Meta:
        label = "Grid"
        icon = "grip"
        template = "grid_block.html"


class EnhancedStandardPage(ModerationMixin, Page):
    base_form_class = ReviewByRequiredOnSubmitForm

    class Meta:
        verbose_name = "Enhanced Standard Page"

    navigation_ribbon = models.ForeignKey(
        NavigationRibbon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    show_floating_definitions_button = models.BooleanField(
        default=False,
        verbose_name="Floating Definitions Button",
        help_text="Check to display the floating definitions button on this page.",
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
                                label="List style",
                            ),
                        ),
                        (
                            "links",
                            blocks.ListBlock(link_obj.child_block, label="Add Entry"),
                        ),
                    ],
                    label="List of Links",
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
            (
                "accordian",
                AccordianBlock(),
            ),
            (
                "callout",
                StyledCalloutBlock(),
            ),
            (
                "quick_access_tiles",
                QuickAccessTilesBlock(),
            ),
            (
                "grid",
                GridBlock(),
            ),
        ],
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("show_floating_definitions_button"),
        FieldPanel("navigation_ribbon"),
        FieldPanel("body"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
