from wagtail import blocks
from wagtail.fields import StreamField, RichTextField
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
    introductory_paragraph = RichTextField(
        blank=True,
        help_text="Optional introductory paragraph for the page.",
        default="The Low-Income Taxpayer Clinics (LITCs) listed are not part of the Internal Revenue Service (IRS) or the United States Tax Court. The Tax Court does not endorse or recommend any specific tax clinic or organization. LITCs located next to the State and City/Place of Trial are available to assist eligible taxpayers.",
    )

    introductory_paragraph_new = blocks.StreamBlock(
        [
            (
                "paragraph",
                blocks.RichTextBlock(
                    help_text="Write your paragraph here.",
                    default="The Low-Income Taxpayer Clinics (LITCs) listed are not part of the Internal Revenue Service (IRS) or the United States Tax Court. The Tax Court does not endorse or recommend any specific tax clinic or organization. LITCs located next to the State and City/Place of Trial are available to assist eligible taxpayers.",
                ),
            ),
        ],
        required=False,
        max_num=1,
        help_text="You can add up to one paragraph here.",
    )

    low_income_taxpayer_clinics = StreamField(
        [("state", LITCStateBlock())],
        use_json_field=True,
        blank=True,
    )

    # Asterisks name is the temporary name
    asterisks_information = blocks.StreamBlock(
        [
            ("paragraph", blocks.RichTextBlock(help_text="Write your paragraph here.")),
        ],
        required=False,
        max_num=2,
        help_text="You can add up to two paragraphs here.",
    )

    promote_panels = custom_promote_panels

    content_panels = Page.content_panels + [
        FieldPanel("introductory_paragraph"),
        # FieldPanel("asterisks_information"),
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
