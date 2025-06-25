from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.search import index

from home.models.pages.enhanced_standard import EnhancedStandardPage
from datetime import date


class InternshipSectionBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(form_classname="title")
    paragraph = blocks.RichTextBlock()


class InternshipPositionBlock(blocks.StructBlock):
    description = blocks.RichTextBlock(required=False)
    section = InternshipSectionBlock(required=False)
    paragraph = blocks.RichTextBlock(
        required=False, help_text="A simple paragraph of text."
    )
    display_from = blocks.DateBlock(
        required=False, help_text="Start displaying this internship"
    )
    closing_date = blocks.DateBlock(
        required=False, help_text="Closing date for this internship"
    )
    external_link = blocks.URLBlock(
        required=False, help_text="Link to external internship posting"
    )

    class Meta:
        label = "Internship Position"
        icon = "user"


class InternshipPrograms(EnhancedStandardPage):
    internship_programs = StreamField(
        [
            ("h2", blocks.CharBlock(label="Heading 2")),
            ("paragraph", blocks.RichTextBlock()),
            ("internship", InternshipPositionBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Internship Programs Details",
    )

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("internship_programs"),
    ]

    search_fields = EnhancedStandardPage.search_fields + [
        index.SearchField("internship_programs"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        today = date.today()

        filtered_blocks = []
        has_active_internship = False

        for block in self.internship_programs:
            if block.block_type == "internship":
                display_from = block.value.get("display_from")
                closing_date = block.value.get("closing_date")

                if display_from <= today and closing_date >= today:
                    has_active_internship = True
                    filtered_blocks.append(block)

            elif block.block_type in ["h2", "paragraph"]:
                filtered_blocks.append(block)

        if has_active_internship:
            context["active_internships"] = filtered_blocks
        else:
            context["active_internships"] = []
            context["no_opportunities_message"] = (
                "There are currently no internship opportunities at the Court. "
                "Please check back at a later time."
            )

        return context
