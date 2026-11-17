from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.blocks import StructBlockValidationError

from home.models.config import IconCategories
from home.models.custom_blocks.page_selector import PageSelectorBlock


class IconHeaderBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        choices=[
            (icon.value, icon.name.replace("_", " ").title()) for icon in IconCategories
        ],
        required=True,
        label="Icon",
    )
    text = blocks.CharBlock(required=True, label="Header Text")

    class Meta:
        label = "Icon Header"
        icon = "title"


class SectionHeaderValue(blocks.StructValue):
    def link_href(self):
        """Resolve the chosen Link URL (internal page or external URL) to an href."""
        link_url = self.get("link_url")
        if not link_url:
            return ""
        selection = link_url[0]
        if selection.block_type == "internal_page":
            return selection.value.url if selection.value else ""
        return selection.value


class SectionHeaderBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True, label="Heading")
    style = blocks.ChoiceBlock(
        choices=[
            ("default", "Default"),
            ("blue_bar", "Blue Bar"),
        ],
        default="default",
        required=True,
        label="Style",
        help_text="Blue Bar displays white heading text on a full-width blue background.",
    )
    link_text = blocks.CharBlock(
        required=False,
        label="Link Text",
        help_text="Optional, but required if a Link URL is chosen. "
        "The link is only saved and displayed when both Link Text and Link URL are provided.",
    )
    link_url = PageSelectorBlock(
        required=False,
        max_num=1,
        label="Link URL",
        help_text="Optional, but required if Link Text is entered. "
        "Choose an internal page or enter an external URL.",
    )

    def clean(self, value):
        result = super().clean(value)
        has_text = bool(result.get("link_text"))
        has_url = bool(result.get("link_url"))
        if has_text and not has_url:
            raise StructBlockValidationError(
                block_errors={
                    "link_url": ValidationError(
                        "A Link URL is required when Link Text is provided."
                    )
                }
            )
        if has_url and not has_text:
            raise StructBlockValidationError(
                block_errors={
                    "link_text": ValidationError(
                        "Link Text is required when a Link URL is chosen."
                    )
                }
            )
        return result

    class Meta:
        label = "Section Header"
        icon = "title"
        template = "section_header_block.html"
        value_class = SectionHeaderValue
