from wagtail import blocks
from django.core.exceptions import ValidationError


class WarningCalloutBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(required=False)

    def clean(self, value):
        value = super().clean(value)
        heading = value.get("heading")
        text = value.get("text")

        if not heading and not text:
            return value

        errors = {}
        if not heading:
            errors["heading"] = ValidationError("This field is required.")
        if not text:
            errors["text"] = ValidationError("This field is required.")
        if errors:
            raise blocks.StructBlockValidationError(block_errors=errors)

        return value


class DetailedTimelinePhaseBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text="Text to be displayed at the beginning of the phase.",
    )

    default_to_open = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Open by Default",
    )

    date_range = blocks.CharBlock(
        max_length=255,
        required=False,
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
                    "text",
                    blocks.RichTextBlock(
                        required=True,
                    ),
                ),
                (
                    "subtext",
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
                    "icon",
                    blocks.ChoiceBlock(
                        choices=[("outbound", "Action"), ("help", "Question")],
                        default="outbound",
                        required=True,
                        help_text="Choose the icon to be displayed in front of the text.",
                        label="Icon",
                    ),
                ),
                (
                    "information",
                    blocks.RichTextBlock(
                        help_text="Helpful Information text", label="Information"
                    ),
                ),
                (
                    "information_subtext",
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

    show_title = blocks.BooleanBlock(
        required=False,
        default=True,
        label="Show Timeline Title",
    )

    warning_callout = WarningCalloutBlock(
        required=False,
        label="Warning Callout",
    )

    show_numbers_in_bubbles = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Bubble Line Numbers?",
        help_text="Check to display a Phase's place within the timeline inside its adjacent bubble.",
    )

    phases = blocks.StreamBlock(
        [("phase", DetailedTimelinePhaseBlock())],
        blank=True,
        help_text="Phases to be displayed in the detailed timeline.",
    )

    class Meta:
        icon = "time"
        label = "Detailed Timeline"
