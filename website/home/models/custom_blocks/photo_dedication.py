from wagtail import blocks
from wagtail.images.blocks import ImageBlock


class PhotoDedicationBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=True)
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
            ("left", "Left (image on left on large screens, top on mobile)"),
            ("right", "Right (image on right on large screens, bottom on mobile)"),
        ],
        default="left",
        required=False,
        help_text="Choose whether the image appears on the left or right on large screens.",
    )

    class Meta:
        icon = "image"
        label = "Photo Dedication"
