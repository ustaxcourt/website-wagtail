from wagtail import blocks
from wagtail.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock

from home.blocks import PDFDocumentChooserBlock


# photo+text block for dedication section on dawson page and enhanced standard page
class PhotoDedicationBlock(blocks.StructBlock):
    image_position = blocks.ChoiceBlock(
        choices=[
            ("left", "Before"),
            ("right", "After"),
        ],
        default="left",
        help_text="Place the image before (left on desktop) or after (right on desktop) the text.",
    )
    title = blocks.CharBlock(
        max_length=255,
        required=False,
        help_text="Optional heading displayed above the photo and text.",
    )
    photo = ImageChooserBlock(
        required=True, help_text="Upload an image to display with this dedication"
    )
    alt_text = blocks.CharBlock(
        required=True,
        max_length=255,
        help_text="Describe the image for a visually impaired person.",
    )
    paragraph_text = blocks.RichTextBlock(
        required=False,
        help_text="Add the main paragraph text for the dedication section",
    )
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
        label = "Photo + Text"
