from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.models.custom_blocks.common import custom_promote_panels
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface

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


class PlacesOfTrialPage(ModerationMixin, Page):
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

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("places_of_trial"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        sorted_places = []

        # Now we will order the states alphabetically and the cities within each state alphabetically as well
        ordered_states = sorted(
            self.places_of_trial, key=lambda x: x.value["state"].lower()
        )
        for state_block in ordered_states:
            ordered_cities = sorted(
                state_block.value["cities"], key=lambda x: x["name"].lower()
            )

            sorted_places.append(
                {
                    "state": state_block.value["state"],
                    "cities": ordered_cities,
                }
            )

        context["sorted_places"] = sorted_places
        return context
