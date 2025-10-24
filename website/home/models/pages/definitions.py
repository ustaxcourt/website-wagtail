from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.models.custom_blocks.common import custom_promote_panels
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from collections import defaultdict


class DefinitionBlock(blocks.StructBlock):
    question = blocks.CharBlock(
        label="Definition Name", help_text="The term being defined"
    )
    answer = blocks.RichTextBlock(
        label="Definition",
        help_text="The definition of the term (supports rich text and links)",
    )

    class Meta:
        icon = "help"
        label = "Definition Entry"


class DefinitionsPage(ModerationMixin, Page):
    definitions = StreamField(
        [("definition", DefinitionBlock())],
        use_json_field=True,
        blank=True,
    )

    promote_panels = custom_promote_panels

    content_panels = Page.content_panels + [
        FieldPanel("definitions"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("definitions"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Group definitions by first letter
        grouped_definitions = defaultdict(list)

        for block in self.definitions:
            if block.block_type == "definition":
                question = block.value.get("question", "")
                if question:
                    first_letter = question[0].upper()
                    grouped_definitions[first_letter].append(block.value)

        # Sort definitions within each group alphabetically
        for letter in grouped_definitions:
            grouped_definitions[letter] = sorted(
                grouped_definitions[letter], key=lambda x: x.get("question", "").lower()
            )

        # Convert to sorted list of tuples for template
        context["grouped_definitions"] = sorted(grouped_definitions.items())
        context["available_letters"] = sorted(grouped_definitions.keys())

        return context
