from wagtail import blocks

from home.models.config import IconCategories


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
    link_text = blocks.CharBlock(required=False, label="Link Text")
    link_url = blocks.URLBlock(required=False, label="Link URL")

    class Meta:
        label = "Section Header"
        icon = "title"
        template = "section_header_block.html"
