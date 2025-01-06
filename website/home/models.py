from django import forms
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("entries", label="Entries"),
    ]


@register_setting
class Footer(BaseGenericSetting):
    technicalQuestions = RichTextField(
        blank=True, help_text="Content for technical questions."
    )
    otherQuestions = RichTextField(blank=True, help_text="Content for other questions.")

    content_panels = Page.content_panels + [
        FieldPanel("technicalQuestions"),
        FieldPanel("otherQuestions"),
    ]


class HomePageEntry(models.Model):
    homepage = ParentalKey("HomePage", related_name="entries", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
    ]


class NavigationCategories(models.TextChoices):
    NONE = "NONE", "None"
    ABOUT_THE_COURT = "ABOUT", "About the Court"
    RULES_AND_GUIDANCE = "RULES", "Rules and Guidance"
    ORDERS_AND_OPINIONS = "ORDERS", "Orders and Opinions"
    eFILING_AND_CASE_MAINTENANCE = "eFILING", "eFiling and Case Maintenance"


class NavigationMixin(Page):
    class Meta:
        abstract = True

    no_index = models.BooleanField(default=False)

    navigation_category = models.TextField(
        max_length=45,
        choices=NavigationCategories.choices,
        default=NavigationCategories.NONE,
    )

    promote_panels = Page.promote_panels + [
        FieldPanel("navigation_category", widget=forms.Select)
    ]


class StandardPage(NavigationMixin):
    class Meta:
        abstract = False

    body = RichTextField(blank=True, help_text="Insert text here.")

    content_panels = Page.content_panels + [FieldPanel("body")]
