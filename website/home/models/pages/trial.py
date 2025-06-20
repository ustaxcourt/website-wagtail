from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.models.custom_blocks.common import custom_promote_panels

from home.models.custom_blocks.alert_message import AlertMessageBlock


class TrialCityBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    note = blocks.TextBlock(required=False)
    address = blocks.CharBlock(
        required=False, help_text="Street address or location name"
    )

    class Meta:
        icon = "home"
        label = "Trial City"


class TrialStateBlock(blocks.StructBlock):
    state = blocks.CharBlock()
    cities = blocks.ListBlock(TrialCityBlock())


class PlacesOfTrialPage(Page):
    places_of_trial = StreamField(
        [("state", TrialStateBlock())],
        use_json_field=True,
        blank=True,
    )
    body = StreamField(
        [
            ("text", blocks.RichTextBlock()),
            ("alert_message", AlertMessageBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    promote_panels = custom_promote_panels

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("places_of_trial"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("places_of_trial"),
    ]
