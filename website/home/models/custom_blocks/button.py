from wagtail import blocks
from home.blocks import SVGDocumentChooserBlock, PDFDocumentChooserBlock
from wagtail.blocks import PageChooserBlock
import xml.etree.ElementTree as ET


class IsIconSvgWithWhiteFillStructValue(blocks.StructValue):
    def is_icon_svg_with_white_fill(self) -> bool:
        """
        Checks if an SVG file contains a 'fill' attribute with a value of "white" in its elements.

        Returns:
            bool: True if 'fill' attribute with white value is found, False otherwise.
        """
        print("is_icon_svg_with_fill called.\n")
        icon = self.get("icon")
        if not icon:
            return False

        icon_url = icon.url
        if not icon_url or icon_url[-4:].lower() != ".svg":
            return False

        try:
            # Parse SVG XML
            tree = ET.parse(icon.file)
            root = tree.getroot()

            # Search for any element with a 'fill' attribute with white value
            for elem in root.iter():
                if "fill" in elem.attrib and (
                    elem.attrib["fill"] == "white" or elem.attrib["fill"] == "#FFFFFF"
                ):
                    return True  # Found a fill attribute with white value

            return False  # No white fill found

        except ET.ParseError as e:
            print(f"Error parsing SVG: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False


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
        value_class = IsIconSvgWithWhiteFillStructValue
