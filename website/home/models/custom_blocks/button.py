from wagtail import blocks
from home.blocks import SVGDocumentChooserBlock, PDFDocumentChooserBlock
from wagtail.blocks import PageChooserBlock


class ButtonBlock(blocks.StructBlock):
    icon = SVGDocumentChooserBlock(required=False, help_text="Optional: Button icon")
    icon_location = blocks.ChoiceBlock(
        choices=[("before", "Before Text"), ("after", "After Text")],
        default="before",
        help_text="Choose the location of the icon relative to the text, if icon is selected.",
    )
    text = blocks.CharBlock(required=True, help_text="Button text", max_length=64)
    url = blocks.StreamBlock(
        [
            ("internal_page", PageChooserBlock(help_text="Select a page to link to")),
            (
                "internal_pdf",
                PDFDocumentChooserBlock(help_text="Select a PDF to link to"),
            ),
            ("external_url", blocks.URLBlock(help_text="Enter an external URL")),
        ],
        max_num=1,
        min_num=1,
        help_text="Select exactly one: Internal Page, External URL, or PDF.",
        label="URL",
    )

    style = blocks.ChoiceBlock(
        choices=[("primary", "Primary"), ("inverted-primary", "Inverted Primary")],
        default="primary",
        help_text="Choose the button style",
    )

    button_hover = blocks.BooleanBlock(
        required=False, help_text="Enable hover effect on button", default=True
    )

    def clean(self, value):
        result = super().clean(value)
        return result

    class Meta:
        icon = "placeholder"
        label = "Button"
