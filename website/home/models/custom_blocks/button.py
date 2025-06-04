from wagtail import blocks


class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text="Button text")
    href = blocks.CharBlock(
        required=True, help_text="Button link  (Can be relative or absolute)"
    )
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
        ],
        default="primary",
        help_text="Choose the button style",
    )

    class Meta:
        icon = "placeholder"
        label = "Button"
