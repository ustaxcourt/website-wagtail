from wagtail import blocks
from home.models.custom_blocks.link import LinkBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


link_obj = blocks.ListBlock(LinkBlock())

custom_promote_panels = [
    MultiFieldPanel(
        [
            FieldPanel("slug"),
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
        ],
        heading="For search engines",
    ),
]


class CommonBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(label="Heading 2")
    h3 = blocks.CharBlock(label="Heading 3")
    hr = blocks.BooleanBlock(
        label="Horizontal Rule",
        default=True,
        help_text="Add Horizontal Rule.",
    )
    h2WithAnchorTag = blocks.StructBlock(
        [
            ("text", blocks.CharBlock()),
            ("anchortag", blocks.CharBlock(required=False)),
        ],
        label="Heading 2 with Anchor Tag",
        help_text="Heading 2 with optional anchor tag for linking",
    )
    clickableButton = blocks.StructBlock(
        [
            ("text", blocks.CharBlock()),
            ("url", blocks.CharBlock(required=False)),
        ],
        label="Clickable Button",
    )
    links = blocks.StructBlock(
        [
            (
                "style",
                blocks.ChoiceBlock(
                    choices=[
                        ("indented", "Indented"),
                        ("unindented", "Unindented"),
                    ],
                    default="indented",
                ),
            ),
            # Reuse your link_obj here
            ("links", link_obj),
        ],
        label="Links",
    )


class ColumnBlock(blocks.StructBlock):
    column = blocks.ListBlock(CommonBlock())
