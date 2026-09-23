from wagtail import blocks

from home.models.custom_blocks.nested_list import create_nested_list_block
from home.models.config import IconCategories


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
    id = blocks.CharBlock(
        required=False,
        help_text="Optional ID for linking to this heading",
    )

    class Meta:
        label = "Heading"


class PrintableSectionBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        choices=[
            (icon.value, icon.name.replace("_", " ").title()) for icon in IconCategories
        ],
        required=False,
        label="Icon",
        help_text="Optional icon displayed beside the printable section title",
    )
    title = blocks.CharBlock(
        required=True, help_text="Title displayed above the printable content"
    )
    intro = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Optional intro text displayed below the title",
    )
    body = blocks.StreamBlock(
        [
            ("heading", PrintableSectionHeadingBlock()),
            ("list", create_nested_list_block(max_depth=4)),
            ("paragraph", blocks.RichTextBlock()),
        ],
        required=True,
        help_text="The content that will be printed",
    )

    class Meta:
        label = "Printable Section"
        icon = "doc-full"
        template = "printable_section_block.html"
