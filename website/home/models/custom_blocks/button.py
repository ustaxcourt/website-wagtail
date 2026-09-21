import logging

from wagtail import blocks
from home.blocks import SVGDocumentChooserBlock, PDFDocumentChooserBlock
from home.models.config import IconCategories
from wagtail.blocks import PageChooserBlock
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def _button_url_block():
    return blocks.StreamBlock(
        [
            ("internal_page", PageChooserBlock(help_text="Select a page to link to")),
            (
                "internal_pdf",
                PDFDocumentChooserBlock(help_text="Select a PDF to link to"),
            ),
            ("external_url", blocks.URLBlock(help_text="Enter an external URL")),
            ("email", blocks.EmailBlock(help_text="Enter an email address")),
            (
                "phone",
                blocks.CharBlock(
                    help_text="Enter a phone number, e.g. (202) 521-0700",
                    max_length=20,
                ),
            ),
        ],
        max_num=1,
        min_num=1,
        help_text="Select exactly one: Internal Page, External URL, PDF, Email, or Phone.",
        label="URL",
    )


class IsIconSvgWithWhiteFillStructValue(blocks.StructValue):
    def is_icon_svg_with_white_fill(self) -> bool:
        """
        Checks if an SVG file contains a 'fill' attribute with a value of "white" in its elements.

        Returns:
            bool: True if 'fill' attribute with white value is found, False otherwise.
        """
        logger.debug("is_icon_svg_with_fill called.")
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
            logger.exception("Error parsing SVG: %s", e)
            return False
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            return False


class ButtonBlock(blocks.StructBlock):
    icon = SVGDocumentChooserBlock(required=False, help_text="Optional: Button icon")
    icon_location = blocks.ChoiceBlock(
        choices=[("before", "Before Text"), ("after", "After Text")],
        default="before",
        help_text="Choose the location of the icon relative to the text, if icon is selected.",
    )
    text = blocks.CharBlock(required=True, help_text="Button text", max_length=64)
    url = _button_url_block()

    style = blocks.ChoiceBlock(
        choices=[("primary", "Primary"), ("inverted-primary", "Inverted Primary")],
        default="primary",
        help_text="Choose the button style",
    )

    button_hover = blocks.BooleanBlock(
        required=False, help_text="Enable hover effect on button", default=True
    )

    helper_text = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="Optional secondary line displayed under the button/link text (e.g. business hours).",
    )

    def clean(self, value):
        result = super().clean(value)
        return result

    class Meta:
        icon = "placeholder"
        label = "Button"
        value_class = IsIconSvgWithWhiteFillStructValue


class SideCardLinkBlock(blocks.StructBlock):
    """
    A link entry for SideCard.links (WAG-1339). Unlike ButtonBlock, icon is a
    fixed dropdown (Material Symbols name, same set as SideCard.icon) rather
    than an arbitrary uploaded SVG - avoids re-uploading a document per icon
    and lets side_card.html render contact/button/plain_links styles without
    caring about SVG fill colors.
    """

    icon = blocks.ChoiceBlock(
        choices=[
            (icon.value, icon.name.replace("_", " ").title()) for icon in IconCategories
        ],
        required=False,
        default=IconCategories.NONE,
        label="Icon",
        help_text="Optional icon for this link.",
    )
    icon_location = blocks.ChoiceBlock(
        choices=[("before", "Before Text"), ("after", "After Text")],
        default="before",
        help_text="Choose the location of the icon relative to the text, if icon is selected.",
    )
    text = blocks.CharBlock(required=True, help_text="Link text", max_length=64)
    url = _button_url_block()

    style = blocks.ChoiceBlock(
        choices=[("primary", "Primary"), ("inverted-primary", "Inverted Primary")],
        default="primary",
        help_text="Choose the button style (used when the card's link display style is 'button').",
    )

    button_hover = blocks.BooleanBlock(
        required=False, help_text="Enable hover effect on button", default=True
    )

    helper_text = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="Optional secondary line displayed under the link text (e.g. business hours).",
    )

    class Meta:
        icon = "placeholder"
        label = "Side Card Link"
