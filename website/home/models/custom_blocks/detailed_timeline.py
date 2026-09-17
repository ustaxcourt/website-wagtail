from wagtail import blocks
from wagtail.admin.panels import FieldPanel


class DetailedTimelinePhaseBlock(blocks.StructBlock):
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

    class Meta:
        label = "Phase"


class DetailedTimelineBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text="Text to be displayed at the beginning of the detailed timeline.",
    )

    introduction = blocks.RichTextBlock(
        help_text="Text to be displayed under the detailed timeline's title.",
        required=True,
    )

    phases = blocks.StreamBlock(
        [("phase", DetailedTimelinePhaseBlock())],
        blank=True,
        help_text="Phases to be displayed in the detailed timeline.",
    )

    class Meta:
        icon = "time"
        label = "Detailed Timeline"
