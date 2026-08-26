from wagtail import blocks


class PrintableRichTextBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=True, help_text="Title displayed above the printable content"
    )
    intro = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Optional intro text displayed below the title",
    )
    content = blocks.RichTextBlock(
        required=True, help_text="The content that will be printed"
    )

    class Meta:
        label = "Printable Rich Text"
        icon = "doc-full"
        template = "printable_rich_text_block.html"
