from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from home.models.pages.enhanced_standard import EnhancedStandardPage
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from home.models.custom_blocks.common import custom_promote_panels
from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitForm
from home.models.snippets.call_to_action import CallToActionBox


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
