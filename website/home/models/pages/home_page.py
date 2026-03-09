from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail import blocks

from django.utils import timezone
from django import forms
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.common import custom_promote_panels
from home.models.snippets.news_item import NewsItem
from home.blocks import SVGChooserBlock
from home.models.pages.press_release import PressReleasePage

import logging
import os
from django.conf import settings


class HomePageAdminForm(WagtailAdminPageForm):
    def clean_intro_text(self):
        value = self.cleaned_data.get("intro_text")
        if not value or not str(value).strip():
            raise forms.ValidationError(
                "Intro text cannot be empty or only whitespace."
            )
        return value


class QuickAccessTileBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=True, help_text="Tile text")
    description = blocks.CharBlock(max_length=255, required=True, help_text="Tile text")
    icon = SVGChooserBlock(required=True)

    related_page = blocks.PageChooserBlock(
        required=False,
    )

    external_url = blocks.URLBlock(required=False, help_text="External link URL")

    class Meta:
        label = "Quick Access Tile"


class FullWidthQuickAccessTileBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=True, help_text="Tile text")
    icon = SVGChooserBlock(required=True)

    related_page = blocks.PageChooserBlock(
        required=False,
    )

    external_url = blocks.URLBlock(required=False, help_text="External link URL")

    class Meta:
        label = "Quick Access Tile"


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
    base_form_class = HomePageAdminForm

    intro_text = models.CharField(
        max_length=255,
        default="Welcome to the United States Tax Court",
        help_text="Main welcome title displayed on the homepage hero section",
    )
    hero_body = RichTextField(
        blank=True,
        default="We are a national court that helps quickly resolve disputes between taxpayers "
        "and the IRS. Our online system, DAWSON allows users to file documents and "
        "track case status. The US Tax Court is an Article I federal trial court "
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

    quick_access_tiles = StreamField(
        [
            ("tile", QuickAccessTileBlock()),
        ],
        blank=True,
        help_text="Add multiple quick access tiles",
    )

    full_width_quick_access_tile = StreamField(
        [
            ("tile", FullWidthQuickAccessTileBlock()),
        ],
        max_num=1,  # This ensures only one can be added
        blank=True,
        use_json_field=True,  # Modern best practice for StreamField
        help_text="Add one optional full-width quick access tile.",
    )

    content_panels = Page.content_panels + [
        # FieldPanel("intro"),
        FieldPanel("intro_text"),
        FieldPanel("hero_body"),
        FieldPanel("hero_background_image"),
        FieldPanel("quick_access_tiles"),
        FieldPanel("full_width_quick_access_tile"),
        FieldPanel("static_text_cards"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    search_fields = Page.search_fields + [
        # index.SearchField("intro"),
        index.SearchField("intro_text"),
        index.SearchField("hero_body"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        logger = logging.getLogger(__name__)
        logger.warning(f"WAGTAILTRANSFER_SOURCES: {settings.WAGTAILTRANSFER_SOURCES}")
        logger.warning(
            f"WAGTAILTRANSFER_SECRET_KEY: {settings.WAGTAILTRANSFER_SECRET_KEY}"
        )
        logger.warning(
            f"WAGTAILTRANSFER_SOURCES_JSON: {settings.WAGTAILTRANSFER_SOURCES_JSON}"
        )
        logger.warning(f"DOMAIN_NAME: {settings.WAGTAILADMIN_BASE_URL}")
        logger.warning(
            f"ENV WAGTAILTRANSFER_SECRET_KEY: {os.getenv('WAGTAILTRANSFER_SECRET_KEY')}"
        )

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

        # Fetch active news items for homepage
        news_items = (
            NewsItem.objects.live()
            .filter(publish_date__lte=now)
            .filter(
                models.Q(homepage_display_expiration_date__gte=now)
                | models.Q(homepage_display_expiration_date__isnull=True)
            )
            .order_by("-publish_date")
        )
        context["news_items"] = news_items

        press_release_page = PressReleasePage.objects.live().first()
        context["press_release_page_url"] = (
            press_release_page.url if press_release_page else "/press-releases/"
        )

        return context
