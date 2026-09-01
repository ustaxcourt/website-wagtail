from wagtail import blocks
from wagtail.admin.panels import FieldPanel


class PhaseBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text="Text to be displayed at the beginning of the phase.",
    )

    date_range = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text="Text to be displayed at the end of the phase.",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("date_range"),
    ]


class SummaryTimelineBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text="Text to be displayed at the beginning of the timeline.",
    )

    phases = blocks.ListBlock(
        PhaseBlock(),
        blank=True,
        help_text="Phases to be displayed in the timeline.",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("phases"),
    ]

    class Meta:
        icon = "time"
        label = "Summary Timeline"
