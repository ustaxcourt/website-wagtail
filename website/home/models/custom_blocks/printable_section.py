from wagtail import blocks

from home.models.config import IconCategories
from home.models.custom_blocks.nested_list import create_nested_list_block


class PrintableSectionHeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock()
    level = blocks.ChoiceBlock(
        choices=[
            ("h2", "Heading 2"),
            ("h3", "Heading 3"),
            ("h4", "Heading 4"),
            ("h5", "Heading 5"),
        ]
    )
    id = blocks.CharBlock(required=False)


class PrintableSectionBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        choices=[
            (icon.value, icon.name.replace("_", " ").title()) for icon in IconCategories
        ],
        required=True,
        default=IconCategories.CHECK,
    )
    title = blocks.CharBlock(required=True)
    intro = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
    )
    body = blocks.StreamBlock(
        [
            ("heading", PrintableSectionHeadingBlock()),
            ("list", create_nested_list_block(max_depth=4)),
            ("paragraph", blocks.RichTextBlock()),
        ],
        required=True,
    )

    class Meta:
        label = "Printable Section"
        icon = "doc-full"
        template = "printable_section_block.html"
