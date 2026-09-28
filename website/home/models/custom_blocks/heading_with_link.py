from wagtail import blocks

from home.models.custom_blocks.button import _button_url_block


class HeadingWithLinkBlock(blocks.StructBlock):
    """
    A heading with a parenthesized link beside it, e.g.
    "Get Started (View detailed timeline)" (WAG-1433). The link sits outside
    the heading element so screen readers don't announce it as part of the
    heading (WAG-1364). The layout lives in heading_with_link_block.html
    rather than rich text, because the rich text editor strips wrapper
    elements and class attributes on save.
    """

    text = blocks.CharBlock(required=True, label="Heading Text")
    level = blocks.ChoiceBlock(
        choices=[
            ("h2", "Heading 2"),
            ("h3", "Heading 3"),
            ("h4", "Heading 4"),
        ],
        default="h2",
    )
    link_text = blocks.CharBlock(
        required=True,
        help_text="Displayed in parentheses after the heading.",
    )
    url = _button_url_block()

    class Meta:
        label = "Heading with Link"
        icon = "title"
        template = "heading_with_link_block.html"
