from datetime import date
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.blocks import DateBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from home.models.pages.enhanced_standard import EnhancedStandardPage


class JudgesRecruiting(EnhancedStandardPage):
    judges_recruiting = StreamField(
        [
            (
                "message",
                blocks.RichTextBlock(
                    required=False,
                    help_text="Default message to display when no judges are recruiting.",
                ),
            ),
            (
                "judge",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            (
                                "judge_name",
                                SnippetChooserBlock(
                                    "home.JudgeProfile", required=False
                                ),
                            ),
                            ("description", blocks.RichTextBlock(blank=True)),
                            (
                                "apply_to_email",
                                blocks.CharBlock(
                                    required=False,
                                    help_text="Enter a valid email.",
                                ),
                            ),
                            (
                                "display_from",
                                DateBlock(
                                    required=False,
                                    help_text="Start displaying from this date",
                                ),
                            ),
                            (
                                "display_to",
                                DateBlock(
                                    required=False,
                                    help_text="Stop displaying after this date",
                                ),
                            ),
                        ]
                    ),
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        help_text="Add judges recruiting details",
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("judges_recruiting"),
    ]

    search_fields = EnhancedStandardPage.search_fields + [
        index.SearchField("judges_recruiting"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        today = date.today()
        # Filter the StreamField content for active judges
        filtered_judges = []
        for block in self.judges_recruiting:
            if block.block_type == "judge":
                for judge in block.value:
                    display_from = judge.get("display_from")
                    display_to = judge.get("display_to")
                    if (not display_from or display_from <= today) and (
                        not display_to or display_to >= today
                    ):
                        filtered_judges.append(judge)
            elif block.block_type == "message":
                message = block.value
                context["message"] = message
        context["judges_recruiting"] = filtered_judges
        return context
