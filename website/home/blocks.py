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
    title = blocks.CharBlock(
        max_length=255, required=True, help_text="Card header (H2)"
    )
    description = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Optional body text",
    )
    icon = SVGChooserBlock(required=True)

    content_alignment = blocks.ChoiceBlock(
        choices=[("center", "Center"), ("left", "Left"), ("right", "Right")],
        default="center",
        required=True,
        help_text="Desktop text alignment (tablet/mobile will be left-aligned per design).",
    )

    link_type = blocks.ChoiceBlock(
        choices=[
            ("related", "Related page"),
            ("external", "External URL"),
        ],
        required=True,
        default="related",
        help_text="Choose what the tile should link to.",
    )

    related_page = blocks.PageChooserBlock(required=False)
    external_url = blocks.URLBlock(required=False, help_text="External link URL")

    def clean(self, value):
        cleaned = super().clean(value)
        link_type = cleaned.get("link_type")
        related_page = cleaned.get("related_page")
        external_url = cleaned.get("external_url")

        errors = {}

        if link_type == "related":
            if not related_page:
                errors["related_page"] = ValidationError(
                    "Please choose a related page."
                )
            # Optional: clear the other field so saved data stays consistent
            cleaned["external_url"] = None

        if link_type == "external":
            if not external_url:
                errors["external_url"] = ValidationError(
                    "Please enter an external URL."
                )
            cleaned["related_page"] = None

        if errors:
            raise blocks.StructBlockValidationError(errors)

        return cleaned

    class Meta:
        label = "Quick Access Tile"
        template = "quick_access_tile_block.html"


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
