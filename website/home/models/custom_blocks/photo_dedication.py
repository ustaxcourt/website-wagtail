from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


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

    class Meta:
        icon = "image"
        label = "Photo Dedication"
