from wagtail import blocks
from home.blocks import SVGChooserBlock


class ButtonBlock(blocks.StructBlock):
    # make icon able to hold images in the future
    icon = SVGChooserBlock(required=False)
    text = blocks.CharBlock(required=True, help_text="Button text")
    href = blocks.CharBlock(
        required=True, help_text="Button link  (Can be relative or absolute)"
    )
    url = blocks.URLBlock(
        required=True, help_text="Optional: Use this field for absolute URLs"
    )
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
        ],
        default="primary",
        help_text="Choose the button style",
    )

    button_hover = blocks.BooleanBlock(
        required=False, help_text="Enable hover effect on button", default=True
    )

    class Meta:
        icon = "placeholder"
        label = "Button"
