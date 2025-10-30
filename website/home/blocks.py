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
