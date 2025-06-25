from home.models.pages.enhanced_standard import EnhancedStandardPage
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


class ReleaseNotes(EnhancedStandardPage):
    """
    A page model for managing release notes with a title, paragraph, and a list of release entries.
    """

    paragraph = RichTextField(
        blank=True, help_text="Introduction or description for the release notes"
    )

    release_entries = StreamField(
        [
            (
                "release_entry",
                blocks.StructBlock(
                    [
                        (
                            "release_date",
                            blocks.DateBlock(
                                required=False, help_text="Date of the release"
                            ),
                        ),
                        (
                            "description",
                            blocks.RichTextBlock(
                                required=False,
                                help_text="Description or details of the release",
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="List of release entries with date and description",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("paragraph"),
        FieldPanel("release_entries"),
    ]

    search_fields = EnhancedStandardPage.search_fields + [
        index.SearchField("paragraph"),
        index.SearchField("release_entries"),
    ]

    class Meta:
        verbose_name = "Release Notes"
        verbose_name_plural = "Release Notes"
