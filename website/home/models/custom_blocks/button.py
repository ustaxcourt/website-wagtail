from wagtail import blocks
from home.blocks import SVGDocumentChooserBlock


class ButtonBlock(blocks.StructBlock):
    # make icon able to hold images in the future
    icon = SVGDocumentChooserBlock(required=False, help_text="Optional: Button icon")
    text = blocks.CharBlock(required=True, help_text="Button text")
    url = blocks.CharBlock(required=True, help_text="Button link", label="URL")
    # url = blocks.URLBlock(
    #     required=True, help_text="Optional: Use this field for absolute URLs"
    # )
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
