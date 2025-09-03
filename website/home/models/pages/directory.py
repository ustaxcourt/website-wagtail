from wagtail import blocks
from home.models.custom_blocks.common import CommonBlock, custom_promote_panels
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.search import index
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface

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


class DirectoryIndex(ModerationMixin, Page):
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

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
