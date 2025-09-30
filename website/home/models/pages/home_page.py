from django.db import models
from django.contrib import messages

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable, ParentalKey
from wagtail.search import index
from wagtail import blocks

from django.utils import timezone
from home.models.custom_blocks.add_entry_custom_button import AddEntryButton
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
        # Hero section panel
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
        context["now"] = timezone.now()
        return context


class HomePageImage(Orderable):
    page = ParentalKey("HomePage", related_name="images", on_delete=models.CASCADE)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("image"),
    ]


class HomePageEntry(Orderable):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=2000, blank=True)
    body = RichTextField(blank=True)
    id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    persist_to_press_releases = models.BooleanField(default=True)

    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()

    def add_entry_above_me(self, sort_order, request):
        try:
            parent = self.homepage.get_latest_revision_as_object()

            new_entry = HomePageEntry(
                homepage=parent,
                title="Insert title ...",
                body="",
                start_date=None,
                end_date=None,
                persist_to_press_releases=True,
            )

            entries = list(parent.entries.order_by("sort_order"))
            current_index = sort_order

            if current_index > -1:
                for i in range(len(entries) - 1, current_index - 1, -1):
                    entry = parent.entries.get(sort_order=i)
                    parent.entries.remove(entry)
                    entry.sort_order += 1
                    parent.entries.add(entry)

                new_entry.sort_order = current_index
                parent.entries.add(new_entry)
                parent.save_revision(user=request.user)

            return new_entry
        except Exception as e:
            messages.error(request, f"Error adding entry above: {str(e)}")
            return None

    panels = [
        AddEntryButton(button_text="Add Entry Above"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("persist_to_press_releases"),
    ]
