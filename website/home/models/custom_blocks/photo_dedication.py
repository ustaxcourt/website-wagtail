from wagtail import blocks
from wagtail.images.blocks import ImageBlock


class PhotoDedicationBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
        required=False,
        help_text="Optional heading displayed above the photo and text.",
    )
    photo = ImageBlock(
        required=False, help_text="Upload an image to display with this dedication"
    )
    paragraph_text = blocks.RichTextBlock(
        required=False,
        help_text="Add the main paragraph text for the dedication section",
    )
    alt_text = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Provide alternative text for the image for accessibility.",
    )
    image_position = blocks.ChoiceBlock(
        choices=[
            ("left", "Before"),
            ("right", "After"),
        ],
        default="left",
        help_text="Place the image before (left on desktop) or after (right on desktop) the text.",
    )

    class Meta:
        icon = "image"
        label = "Photo Dedication"
