from wagtail import blocks
from home.models.custom_blocks.common import CommonBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock


judge_snippet = SnippetChooserBlock(
    target_model="home.JudgeCollection",
    required=False,
    help_text="Optionally pick a JudgeCollection snippet",
    label="Judge Collection",
)


class DirectoryColumnBlock(CommonBlock):
    JudgeCollection = judge_snippet
    DirectoryEntry = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("description", blocks.RichTextBlock()),
                ("phone_number", blocks.CharBlock()),
            ]
        )
    )


class DirectoryIndex(Page):
    template = "home/enhanced_standard_page.html"
    max_count = 1

    body = StreamField(
        [
            ("directory", DirectoryColumnBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Directory entries or judge profiles",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("body"),
    ]
