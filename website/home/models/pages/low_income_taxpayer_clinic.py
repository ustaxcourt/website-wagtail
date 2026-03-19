from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.models.custom_blocks.common import custom_promote_panels
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface


class LITCClinicBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    address = blocks.CharBlock(required=False)
    phone = blocks.CharBlock(required=False)
    website = blocks.URLBlock(required=False)
    email = blocks.EmailBlock(required=False)
    small_case_procedures_only = blocks.BooleanBlock(
        required=False,
        help_text="Indicates the clinic only represents taxpayers who have elected the small tax case procedures.",
    )

    class Meta:
        icon = "user"
        label = "Low Income Taxpayer Clinic"


class LITCCityBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    small_cases_only = blocks.BooleanBlock(
        required=False, help_text="Indicates the city only holds small case trials."
    )
    clinics = blocks.ListBlock(LITCClinicBlock())

    class Meta:
        icon = "home"
        label = "Low Income Taxpayer Clinic City"


class LITCStateBlock(blocks.StructBlock):
    state = blocks.CharBlock()
    cities = blocks.ListBlock(LITCCityBlock())


class LITCPage(ModerationMixin, Page):
    introductory_paragraph = StreamField(
        [
            (
                "paragraph",
                blocks.RichTextBlock(
                    help_text="Write your paragraph here.",
                    default="The Low-Income Taxpayer Clinics (LITCs) listed are not part of the Internal Revenue Service (IRS) or the United States Tax Court. The Tax Court does not endorse or recommend any specific tax clinic or organization. LITCs located next to the State and City/Place of Trial are available to assist eligible taxpayers.",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        default=[
            (
                "paragraph",
                "<p>The Low-Income Taxpayer Clinics (LITCs) listed are not part of the Internal Revenue Service (IRS) or the United States Tax Court. The Tax Court does not endorse or recommend any specific tax clinic or organization. LITCs located next to the State and City/Place of Trial are available to assist eligible taxpayers.</p>",
            ),
        ],
    )

    low_income_taxpayer_clinics = StreamField(
        [("state", LITCStateBlock())],
        use_json_field=True,
        blank=True,
    )

    # Asterisks name is the temporary name
    asterisks_notice = StreamField(
        blocks.StreamBlock(
            [
                # ("One_Asterisks_for_cities", blocks.RichTextBlock(help_text="Write your paragraph here.", default="<p><span style=\"color:#DB0000;\" class=\"small-case-indicator\">*</span> Indicates the city only holds trials for small tax cases.</p>")),
                # ("Two_Asterisks_for_clinics", blocks.RichTextBlock(help_text="Write your paragraph here.", default="<p><span style=\"color:#DB0000;\" class=\"small-case-indicator\">**</span> Indicates the clinic only represents taxpayers who have elected the small tax case procedure</p>")),
                (
                    "asterisk_notice",
                    blocks.StructBlock(
                        [
                            # ("asterisks_count(*)", blocks.IntegerBlock(min_value=0, max_value=2, default=0)),
                            (
                                "asterisks_count",
                                blocks.ChoiceBlock(
                                    choices=[("", "None"), ("*", "*"), ("**", "**")],
                                    default="",
                                    required=False,
                                    help_text="Set the number of asterisks to display (0, 1 or 2).",
                                ),
                            ),
                            (
                                "text",
                                blocks.RichTextBlock(
                                    help_text="Write your explanation text here."
                                ),
                            ),
                        ],
                        icon="info-circle",
                        label="Asterisk Notice",
                    ),
                ),
            ],
            # max_num=2,
        ),
        use_json_field=True,
        blank=True,
        default=[
            # ("One_Asterisks_for_cities", "<p><span style=\"color:#DB0000;\" class=\"small-case-indicator\">*</span> Indicates the city only holds trials for small tax cases.</p>"),
            # ("Two_Asterisks_for_clinics", "<p><span style=\"color:#DB0000;\" class=\"small-case-indicator\">**</span> Indicates the clinic only represents taxpayers who have elected the small tax case procedure</p>"),
            (
                "asterisk_notice",
                {
                    "asterisks_count": "*",
                    "text": "Indicates the city only holds trials for small tax cases.",
                },
            ),
            (
                "asterisk_notice",
                {
                    "asterisks_count": "**",
                    "text": "Indicates the clinic only represents taxpayers who have elected the small tax case procedure.",
                },
            ),
        ],
    )

    promote_panels = custom_promote_panels

    content_panels = Page.content_panels + [
        FieldPanel("introductory_paragraph"),
        FieldPanel("asterisks_notice"),
        FieldPanel("low_income_taxpayer_clinics"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("low_income_taxpayer_clinics"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        data_list = []

        for block in self.low_income_taxpayer_clinics:
            if block.block_type == "state":
                state_val = block.value

                raw_cities = state_val.get("cities", [])
                processed_cities = []

                for city in raw_cities:
                    raw_clinics = city.get("clinics", [])
                    sorted_clinics = sorted(
                        raw_clinics, key=lambda x: x["name"].lower()
                    )

                    city_data = {
                        "name": city.get("name"),
                        "small_cases_only": city.get("small_cases_only"),
                        "note": city.get("note"),
                        "clinics": sorted_clinics,
                    }
                    processed_cities.append(city_data)

                sorted_cities = sorted(
                    processed_cities, key=lambda x: x["name"].lower()
                )

                data_list.append(
                    {"state": state_val.get("state"), "cities": sorted_cities}
                )

        sorted_data = sorted(data_list, key=lambda x: x["state"].lower())

        context["sorted_clinics"] = sorted_data

        return context
