from wagtail.documents.blocks import DocumentChooserBlock
from .widgets import AdminSVGChooser, AdminPDFChooser
from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.contrib.typed_table_block.blocks import (
    TypedTableBlock,
    TypedTableBlockAdapter,
)
from wagtail.admin.telepath import register


class SVGDocumentChooserBlock(DocumentChooserBlock):
    """
    A custom DocumentChooserBlock that uses the AdminSVGChooser widget by default.
    This separates the widget (presentation) from the block's definition (schema).
    """

    widget = AdminSVGChooser()


class PDFDocumentChooserBlock(DocumentChooserBlock):
    """
    A custom DocumentChooserBlock that uses the AdminPDFChooser widget by default.
    Only shows PDF files in the chooser.
    """

    widget = AdminPDFChooser()


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
    title = blocks.CharBlock(
        max_length=255, required=True, help_text="Card header (H2)"
    )
    description = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic"],
        help_text="Optional body text",
    )
    icon = SVGChooserBlock(required=True)

    content_alignment = blocks.ChoiceBlock(
        choices=[("center", "Center"), ("left", "Left"), ("right", "Right")],
        default="center",
        required=True,
        help_text="Desktop text alignment (tablet/mobile will be left-aligned per design).",
    )

    link = blocks.StreamBlock(
        [
            ("related_page", blocks.PageChooserBlock()),
            ("external_url", blocks.URLBlock()),
        ],
        min_num=1,
        max_num=1,
        required=False,
        help_text="Choose where this tile should link.",
    )

    class Meta:
        label = "Quick Access Tile"
        template = "quick_access_tile_block.html"


class RootRelativeURLBlock(blocks.URLBlock):
    def clean(self, value):
        if isinstance(value, str):
            value = value.strip()

        # Protocol-relative URLs (e.g. //example.com) should never be allowed
        # for Judge Index quick-access tiles.
        if isinstance(value, str) and value.startswith("//"):
            raise ValidationError("Enter a valid URL.")

        try:
            return super().clean(value)
        except ValidationError:
            if (
                isinstance(value, str)
                and value.startswith("/")
                and not value.startswith("//")
            ):
                return value
            raise


class JudgeIndexQuickAccessTileBlock(QuickAccessTileBlock):
    link = blocks.StreamBlock(
        [
            ("related_page", blocks.PageChooserBlock()),
            ("external_url", RootRelativeURLBlock()),
        ],
        min_num=1,
        max_num=1,
        required=False,
        help_text="Choose where this tile should link.",
    )


class QuickAccessTilesBlock(blocks.StructBlock):
    tiles_hover_enabled = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="If checked, hover treatment is enabled for ALL tiles in this set.",
    )

    icon_position = blocks.ChoiceBlock(
        choices=[
            ("desktop_top_mobile_left", "Desktop-Top / Mobile-Left"),
            ("desktop_bottom_mobile_right", "Desktop-Bottom / Mobile-Right"),
        ],
        default="desktop_top_mobile_left",
        required=True,
        help_text="Applies to ALL tiles in this set (keeps icon placement uniform).",
    )

    tiles = blocks.ListBlock(
        QuickAccessTileBlock(),
        required=False,
        help_text="Add, reorder, duplicate, or remove tiles. Responsive grid: 3 desktop / 2 tablet / 1 mobile.",
    )

    class Meta:
        label = "Quick Access Tiles"
        icon = "grip"
        template = "quick_access_tiles_block.html"


class JudgeIndexQuickAccessTilesBlock(QuickAccessTilesBlock):
    tiles = blocks.ListBlock(
        JudgeIndexQuickAccessTileBlock(),
        required=False,
        help_text="Add, reorder, duplicate, or remove tiles. Responsive grid: 3 desktop / 2 tablet / 1 mobile.",
    )


class NoCaptionTypedTableBlock(TypedTableBlock):
    """
    TypedTableBlock with the built-in caption field suppressed in the editor.
    The Enhanced Table component manages its own header and caption fields
    at the StructBlock level so they appear above the table widget in the admin.
    The caption input is hidden via CSS injected through wagtail_hooks.
    """

    def value_from_datadict(self, data, files, prefix):
        result = super().value_from_datadict(data, files, prefix)
        result.caption = ""
        return result

    def to_python(self, value):
        result = super().to_python(value)
        result.caption = ""
        return result


class NoCaptionTypedTableBlockAdapter(TypedTableBlockAdapter):
    js_constructor = "wagtail.contrib.typed_table_block.blocks.TypedTableBlock"

    def js_args(self, block):
        return super().js_args(block)


register(NoCaptionTypedTableBlockAdapter(), NoCaptionTypedTableBlock)
