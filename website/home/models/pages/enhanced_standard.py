from django.db import models
from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.blocks import PageChooserBlock, StructBlockValidationError
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock

# from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from home.blocks import SVGDocumentChooserBlock
from home.blocks import QuickAccessTilesBlock
from home.blocks import NoCaptionTypedTableBlock
from home.models.config import IconCategories
from home.models.custom_blocks.button import ButtonBlock
from home.models.custom_blocks.common import link_obj
from home.models.custom_blocks.photo_dedication import PhotoDedicationBlock
from home.models.custom_blocks.image_with_link import ImageWithLinkBlock
from home.models.custom_blocks.common import ColumnBlock
from home.models.snippets.navigation import NavigationRibbon
from home.models.custom_blocks.nested_list import create_nested_list_block
from home.models.custom_blocks.common import custom_promote_panels
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitForm

table_value_types = [
    ("text", blocks.RichTextBlock()),
]


class IndentStyle(models.TextChoices):
    INDENTED = "indented"
    UNINDENTED = "unindented"


FAQ_FILTER_TAG_CHOICES = [
    ("filing", "Filing"),
    ("deadlines", "Deadlines"),
    ("representation", "Representation"),
    ("forms-documents", "Forms & Documents"),
    ("trial-process", "Trial Process"),
    ("fees-costs", "Fees & Costs"),
    ("after-decision", "After Decision"),
]


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


class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255, required=True, help_text="Title user will see before opening"
    )
    description = blocks.StreamBlock(
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
            ("prose", blocks.RichTextBlock()),
            ("callout", StyledCalloutBlock()),
        ],
        required=True,
        help_text="Add text or special elements to the body",
    )
    default_to_open = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Check to have the accordion open by default when the page loads.",
    )

    class Meta:
        label = "Accordion Block"
        template = "accordion_block.html"


new_table_value_types = [
    (
        "components",
        blocks.StreamBlock(
            [
                ("text", blocks.RichTextBlock()),
                ("callout", StyledCalloutBlock()),
                ("accordion", AccordionBlock()),
                ("button", ButtonBlock()),
            ],
            required=False,
        ),
    ),
]


class TableListBlock(blocks.StructBlock):
    header = blocks.CharBlock(
        required=False,
        label="Header",
        help_text="The title displayed above the table (rendered as H2).",
    )
    caption = blocks.RichTextBlock(
        required=False,
        label="Caption",
        features=["bold", "italic", "link"],
        help_text="A caption displayed above or below the table depending on Caption Location.",
    )
    caption_location = blocks.ChoiceBlock(
        choices=[("top", "Top"), ("bottom", "Bottom")],
        default="top",
    )
    style = blocks.ChoiceBlock(
        choices=[
            ("styled", "Styled Table"),
            ("borderlessUnstyled", "Borderless Unstyled Table"),
            ("unstyled", "Unstyled Table"),
        ],
        default="styled",
    )
    fixed = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Check to set table layout to fixed width.",
    )
    table = NoCaptionTypedTableBlock(new_table_value_types)

    class Meta:
        label = "Enhanced Table"
        icon = "table"


class GridCellBlock(blocks.StructBlock):
    header = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Optional header for this grid cell",
    )
    header_color = blocks.ChoiceBlock(
        required=True,
        default="#f1f9fc",
        choices=[
            ("#f1f9fc", "Default"),
            ("#DEEAF0", "Blue-Gray"),
        ],
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


# Base block definitions used in ENHANCED_STANDARD_PAGE_CONTENT
_BASE_BLOCK_TYPES = [
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
    (
        "indented_paragraph",
        blocks.RichTextBlock(
            label="Indented Paragraph",
            help_text="Paragraph with left indentation for alignment with list items",
        ),
    ),
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
    ("image", ImageWithLinkBlock()),
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
    (
        "enhanced_table",
        TableListBlock(),
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
                    (
                        "filtertag",
                        blocks.ChoiceBlock(
                            choices=FAQ_FILTER_TAG_CHOICES,
                            required=False,
                            label="FilterTag",
                        ),
                    ),
                ]
            ),
            label="Question and Answer",
            help_text="Add a question and answer. Link the anchor tag number. Select the FAQ FilterTag type in the dropdown.",
        ),
    ),
    ("columns", ColumnBlock()),
    (
        "embedded_video",
        blocks.StructBlock(
            [
                ("title", blocks.CharBlock(required=False)),
                ("description", blocks.RichTextBlock(required=False)),
                (
                    "video_url",
                    blocks.URLBlock(
                        required=True,
                        help_text="Use the YouTube embed URL (e.g. https://www.youtube.com/embed/VIDEO_ID), not the watch URL.",
                    ),
                ),
                (
                    "text_location",
                    blocks.ChoiceBlock(
                        choices=[("below", "Below"), ("right-of", "Right")],
                        default="below",
                    ),
                ),
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
        "accordion",
        AccordionBlock(),
    ),
    (
        "callout",
        StyledCalloutBlock(),
    ),
    (
        "grid",
        GridBlock(),
    ),
]


class AnchorPageBlock(blocks.StructBlock):
    breadcrumb_title = blocks.CharBlock(required=True, help_text="Button text")
    body = blocks.StreamBlock(
        _BASE_BLOCK_TYPES
        + [
            ("quick_access_tiles", QuickAccessTilesBlock()),
        ],
        required=False,
    )


class CardTileBlock(blocks.StructBlock):
    """Individual card tile with icon and H2 header."""

    icon = SVGDocumentChooserBlock(required=True, help_text="Card Icon")
    icon_direction = blocks.ChoiceBlock(
        required=False,
        help_text="Icon placement, e.g. Top, Right, Bottom, Left. Default is Top.",
        choices=[
            ("top", "Top"),
            ("right", "Right"),
            ("bottom", "Bottom"),
            ("left", "Left"),
        ],
        default="top",
    )
    card_header = blocks.CharBlock(required=True, help_text="Displays the card title")
    link = blocks.StreamBlock(
        [
            ("anchor_page", AnchorPageBlock()),
            ("internal_page", PageChooserBlock()),
            ("external_url", blocks.URLBlock()),
        ],
        max_num=1,
        min_num=1,
    )

    card_hover = blocks.BooleanBlock(
        required=False, help_text="Enable hover effect", default=True
    )

    class Meta:
        label = "Card Tile"
        icon = "doc-full"
        # Set label_format to show card_header in admin for easier identification
        label_format = "Card Tile: {card_header}"


class CardTilesBlock(blocks.StructBlock):
    """
    Card Tiles container - displays up to 4 card tiles in a responsive grid.
    Desktop (>1025px): 4 buttons in a row
    Tablet (768-1025px): 2x2 grid
    Mobile (<768px): Vertical stack
    """

    tiles = blocks.ListBlock(
        CardTileBlock(),
        min_num=1,
        max_num=4,
        help_text="Add up to 4 card tiles. They will display responsively based on screen size.",
    )

    default_content = blocks.StreamBlock(
        _BASE_BLOCK_TYPES,
        required=False,
        help_text="Default content to display when no card is selected",
    )

    show_back_button = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Display a back button when a card tile is selected (e.g. "
        "p/a, p/b). Hidden on the default view showing all card tiles. If "
        "checked, Back Button Text is required.",
    )
    back_button_text = blocks.CharBlock(
        required=False,
        max_length=64,
        help_text="Text shown on the back button. Required if 'Show back "
        "button' is checked.",
    )

    def clean(self, value):
        result = super().clean(value)
        if result["show_back_button"] and not result["back_button_text"]:
            raise StructBlockValidationError(
                block_errors={
                    "back_button_text": ValidationError(
                        "Back Button Text is required when 'Show back button' "
                        "is checked."
                    )
                }
            )
        return result

    class Meta:
        label = "Card Tiles"
        icon = "grip"
        template = "includes/card_tiles.html"


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
        _BASE_BLOCK_TYPES
        + [
            ("card_tiles", CardTilesBlock()),
            ("quick_access_tiles", QuickAccessTilesBlock()),
        ],
        block_counts={
            "card_tiles": {"min_num": 0, "max_num": 1},
        },
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

    def clean(self):
        super().clean()
        # Validate that [internal page] links don't point to this page, as [anchor page] should be selected instead =)
        for block in self.body:
            if block.block_type == "card_tiles":
                for i, tile in enumerate(block.value.get("tiles", [])):
                    for link in tile.get("link", []):
                        if link.block_type == "internal_page" and link.value:
                            if link.value.pk == self.pk:
                                from django.core.exceptions import ValidationError

                                raise ValidationError(
                                    {
                                        "body": f"Card Tile {i + 1}: The link type [Internal Page] should not point to itself. Use [Anchor Page] instead."
                                    }
                                )
