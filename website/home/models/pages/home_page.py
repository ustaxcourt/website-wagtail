from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail import blocks

from django.utils import timezone
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.common import custom_promote_panels


class StaticTextCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=2000, required=False, help_text="Card title")
    body = blocks.RichTextBlock(required=False, help_text="Card content")
    start_date = blocks.DateTimeBlock(
        required=False, help_text="Start date for display"
    )
    end_date = blocks.DateTimeBlock(required=False, help_text="End date for display")

    class Meta:
        label = "Static Text Card"


class HomePage(ModerationMixin, Page):
    # Hero section fields for CMS editing
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")
    hero_title = models.CharField(
        max_length=255,
        default="Welcome to the United States Tax Court",
        help_text="Main welcome title displayed on the homepage hero section",
    )
    hero_body = RichTextField(
        blank=True,
        default="We are a national court that helps quickly resolve disputes between taxpayers "
        "and the IRS. Our online system, DAWSON allows users to file documents and "
        "track case status. The US Tax Court is an Article I federal trail court "
        "established by Congress under Article 1 of the U.S. Constitution, Section 8.",
        help_text="Welcome text displayed below the title in the hero section",
    )
    hero_background_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Background image for the hero section (recommended size: 3000x1200px)",
    )

    static_text_cards = StreamField(
        [
            ("card", StaticTextCardBlock()),
        ],
        blank=True,
        help_text="Add multiple static text cards",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("hero_title"),
        FieldPanel("hero_body"),
        FieldPanel("hero_background_image"),
        FieldPanel("static_text_cards"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("hero_title"),
        index.SearchField("hero_body"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Filter static text cards based on start/end dates
        live_static_text_cards = []
        now = timezone.now()
        for card_block in self.static_text_cards:
            card = card_block.value

            # Check if card should be displayed
            start_valid = not card.get("start_date") or card.get("start_date") <= now
            end_valid = not card.get("end_date") or card.get("end_date") >= now

            if start_valid and end_valid:
                live_static_text_cards.append(card)

        context["live_static_text_cards"] = live_static_text_cards

        return context
