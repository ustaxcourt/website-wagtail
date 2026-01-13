from wagtail.documents.blocks import DocumentChooserBlock
from .widgets import AdminSVGChooser
from django.core.exceptions import ValidationError
from wagtail import blocks


class SVGDocumentChooserBlock(DocumentChooserBlock):
    """
    A custom DocumentChooserBlock that uses the AdminSVGChooser widget by default.
    This separates the widget (presentation) from the block's definition (schema).
    """

    widget = AdminSVGChooser()


class SVGChooserBlock(blocks.StructBlock):
    """A custom block that validates that the selected document is an SVG."""

    svg_file = SVGDocumentChooserBlock(help_text="Select an SVG file.")

    def clean(self, value):
        """
        Adds custom validation to the block. This method is called when the
        form is submitted.
        """
        cleaned_data = super().clean(value)
        chosen_document = cleaned_data.get("svg_file")

        if not chosen_document:
            return cleaned_data

        if not chosen_document.file.name.lower().endswith(".svg"):
            raise ValidationError(
                "Incorrect file type. Please select an SVG file.",
            )

        return cleaned_data

    class Meta:
        label = "SVG Icon"
        icon = "image"


class QuickAccessTileBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=True, help_text="Tile text")
    description = blocks.CharBlock(max_length=255, required=True, help_text="Tile text")
    icon = SVGChooserBlock(required=True)

    icon_position = blocks.ChoiceBlock(
        choices=[
            ("desktop_top_mobile_left", "Desktop-Top / Mobile-Left"),
            ("desktop_bottom_mobile_right", "Desktop-Bottom / Mobile-Right"),
        ],
        default="desktop_top_mobile_left",
        required=True,
        help_text="Position of icon in desktop and mobile layouts",
    )

    tile_hover_enabled = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Enable hover effect on tile",
    )

    content_alignment = blocks.ChoiceBlock(
        choices=[
            ("center", "Center"),
            ("left", "Left"),
            ("right", "Right"),
        ],
        default="center",
        required=True,
        help_text="Alignment of content within the tile",
    )

    related_page = blocks.PageChooserBlock(
        required=False,
    )

    external_url = blocks.URLBlock(required=False, help_text="External link URL")

    class Meta:
        label = "Quick Access Tile"
        template = "quick_access_tile_block.html"


class QuickAccessTilesBlock(blocks.StructBlock):
    """
    A container block for Quick Access Tiles that enables users to add,
    remove, and reorder tiles in a responsive grid layout.
    """

    tiles = blocks.StreamBlock(
        [
            ("tile", QuickAccessTileBlock()),
        ],
        required=False,
        help_text="Add and reorder Quick Access Tiles. Tiles will display in a responsive grid (3 columns on desktop, 2 on tablet, 1 on mobile).",
    )

    class Meta:
        label = "Quick Access Tiles"
        icon = "grip"
        template = "quick_access_tiles_block.html"
