from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Orderable, Page
from wagtail.fields import RichTextField, StreamField
from home.models.pages.enhanced_standard import EnhancedStandardPage
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.search import index
from home.models.config import IconCategories
from home.models.custom_blocks.button import SideCardLinkBlock
from home.models.custom_blocks.common import custom_promote_panels
from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitForm
from home.models.snippets.call_to_action import CallToActionBox


class SideCard(Orderable, ClusterableModel):
    page = ParentalKey(
        "PetitionerExperiencePage", related_name="side_cards", on_delete=models.CASCADE
    )
    icon = models.CharField(
        max_length=200,
        choices=IconCategories.choices,
        blank=True,
        default="",
        help_text="Optional icon for this side card.",
    )
    header_title = models.CharField(max_length=255)
    # Optional: e.g. a plain_links card may be just a header and links.
    introductory_text = RichTextField(blank=True)
    color = models.CharField(
        max_length=20,
        # TODO: we gotta get this list of colors from a central place
        choices=[
            ("white", "White"),
            ("gray", "Gray"),
            ("dark-primary", "Dark-Primary"),
            ("green", "Green"),
            ("yellow", "Yellow"),
            ("blue", "Blue"),
            ("navy", "Navy"),
        ],
        default="white",
    )
    # TODO: one style applies to every link on the card. Move this per-link
    # if a card ever needs to mix styles (e.g. a contact row and a plain link).
    link_display_style = models.CharField(
        max_length=20,
        choices=[
            ("contact", "Contact rows (icon + text in a white pill)"),
            ("button", "Full-width button(s)"),
            ("plain_links", "Plain underlined text links"),
        ],
        default="button",
        help_text="How the links below should be displayed on this card.",
    )
    links = StreamField(
        [("side_card_link", SideCardLinkBlock())],
        blank=True,
        use_json_field=True,
        help_text="Informational blocks/buttons for this side card.",
    )

    panels = [
        FieldPanel("icon"),
        FieldPanel("header_title"),
        FieldPanel("introductory_text"),
        FieldPanel("color"),
        FieldPanel("link_display_style"),
        FieldPanel("links"),
    ]

    def __str__(self):
        return self.header_title


class PetitionerExperienceReviewByRequiredOnSubmitForm(ReviewByRequiredOnSubmitForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["navigation_ribbon"].required = True  # Force required in admin


class PetitionerExperiencePage(EnhancedStandardPage):
    template = "home/petitioner_experience_page.html"
    base_form_class = PetitionerExperienceReviewByRequiredOnSubmitForm

    class Meta:
        verbose_name = "Petitioner Experience Page"

    introductory_text = RichTextField(
        help_text="Text to be displayed at the top of the page under the page's title.",
        blank=True,
    )

    call_to_action = models.ForeignKey(
        CallToActionBox,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("show_floating_definitions_button"),
        FieldPanel("navigation_ribbon"),
        FieldPanel("introductory_text"),
        FieldPanel("body"),
        FieldPanel("call_to_action"),
        InlinePanel("side_cards", label="Side Cards"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = EnhancedStandardPage.search_fields + [
        index.SearchField("introductory_text"),
    ]

    def clean(self):
        super().clean()
        if not self.navigation_ribbon_id:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {"navigation_ribbon": "Navigation Ribbon is required."}
            )
