from wagtail import blocks


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
        label="Date Range",
    )

    instructions = blocks.RichTextBlock(
        required=True,
        help_text="Text to be shown at the top of the phase when it is expanded.",
    )

    your_tasks = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "Text",
                    blocks.RichTextBlock(
                        required=True,
                    ),
                ),
                (
                    "Subtext",
                    blocks.RichTextBlock(
                        required=False,
                    ),
                ),
            ],
            label="Task Item",
        ),
        required=False,
        label="Your Tasks",
        default=[],
        help_text="Tasks to be completed during this phase.",
    )

    helpful_information = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "Icon",
                    blocks.ChoiceBlock(
                        choices=[("outbound", "Action"), ("help", "Question")],
                        default="Action",
                        required=True,
                        help_text="Choose the icon to be displayed in front of the text.",
                        label="Icon",
                    ),
                ),
                (
                    "Information",
                    blocks.RichTextBlock(
                        help_text="Helpful Information text", label="Information"
                    ),
                ),
                (
                    "InformationSubtext",
                    blocks.RichTextBlock(
                        help_text="Helpful Information subtext",
                        label="Information Subtext",
                        required=False,
                    ),
                ),
            ],
            label="Helpful Information Item",
        ),
        required=False,
        label="Helpful Information",
        default=[],
        help_text="Helpful information to be displayed at the bottom of the phase when expanded.",
    )

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
