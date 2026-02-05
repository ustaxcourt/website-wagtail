from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.models.custom_blocks.common import custom_promote_panels
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface

from home.models.custom_blocks.alert_message import AlertMessageBlock


class LITCClinicBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    address = blocks.CharBlock(required=False)
    email = blocks.EmailBlock(required=False)
    phone = blocks.CharBlock(required=False)
    website = blocks.URLBlock(required=False)
    small_case_procedures_only = blocks.BooleanBlock(
        required=False, help_text="Indicates if the clinic handles only small cases"
    )

    class Meta:
        icon = "user"
        label = "Low Income Taxpayer Clinic"


class LITCCityBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    small_cases_only = blocks.BooleanBlock(
        required=False, help_text="Indicates if the clinic handles only small cases"
    )
    clinics = blocks.ListBlock(LITCClinicBlock())

    class Meta:
        icon = "home"
        label = "Low Income Taxpayer Clinic City"


class LITCStateBlock(blocks.StructBlock):
    state = blocks.CharBlock()
    cities = blocks.ListBlock(LITCCityBlock())


class LITCPage(ModerationMixin, Page):
    low_income_taxpayer_clinics = StreamField(
        [("state", LITCStateBlock())],
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
        FieldPanel("low_income_taxpayer_clinics"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("low_income_taxpayer_clinics"),
    ]
