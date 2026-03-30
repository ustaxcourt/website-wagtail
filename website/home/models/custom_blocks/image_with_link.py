from wagtail import blocks
from wagtail.blocks import PageChooserBlock
from wagtail.images.blocks import ImageBlock

from home.blocks import PDFDocumentChooserBlock


class ImageWithLinkBlock(blocks.StructBlock):
    image = ImageBlock()
    link = blocks.StreamBlock(
        [
            ("internal_page", PageChooserBlock(help_text="Select a page to link to")),
            (
                "internal_pdf",
                PDFDocumentChooserBlock(help_text="Select a PDF to link to"),
            ),
            ("external_url", blocks.URLBlock(help_text="Enter an external URL")),
        ],
        max_num=1,
        min_num=0,
        required=False,
        help_text="Optional: add a link to make the image clickable.",
    )

    class Meta:
        icon = "image"
        label = "Image"
