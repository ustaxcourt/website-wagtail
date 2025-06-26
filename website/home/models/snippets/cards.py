"""
Card snippet models for the website.

This module contains SimpleCard and FancyCard snippet models with
draft and moderation workflow capabilities.
"""

from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
    PublishingPanel,
)
from wagtail.models import DraftStateMixin, RevisionMixin, WorkflowMixin, ParentalKey
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.query import PageQuerySet


class RelatedPage(models.Model):
    """Model to store multiple related pages for a SimpleCard."""

    card = ParentalKey(
        "SimpleCard", related_name="related_pages", on_delete=models.CASCADE
    )
    display_title = models.CharField(
        max_length=255,
        help_text="Optional title to display in link",
        blank=True,
    )
    related_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional URL to link to when the card is clicked.",
    )

    panels = [
        FieldPanel("display_title"),
        PageChooserPanel("related_page"),
        FieldPanel("url"),
    ]


@register_snippet
class SimpleCard(WorkflowMixin, DraftStateMixin, RevisionMixin, ClusterableModel):
    """A Simple Card snippet that contains optional title, icon, and related pages."""

    card_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The title to appear at the top of the card",
    )
    card_icon = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Icon Name - see https://fontawesome.com/icons/ and enter the name of the icon (i.e. "accessible")',
    )

    # Enable search indexing
    search_fields = [
        index.SearchField("card_title"),
    ]

    # Use PageQuerySet manager for live/draft filtering
    objects = PageQuerySet.as_manager()

    # Define panels for the admin interface
    panels = [
        FieldPanel("card_title"),
        FieldPanel("card_icon"),
        InlinePanel("related_pages", label="Related Pages"),
        PublishingPanel(),
    ]

    def __str__(self):
        return self.card_title if self.card_title else f"Simple Card #{self.pk}"

    class Meta:
        ordering = ["card_title"]
        verbose_name = "Simple Card"
        verbose_name_plural = "Simple Cards"


@register_snippet
class FancyCard(WorkflowMixin, DraftStateMixin, RevisionMixin, ClusterableModel):
    """A Fancy Card snippet with photo and text content."""

    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image to display with in dark blue card.",
    )

    url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The URL to link to when the photo is clicked.",
    )

    text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The text to appear next to the image in the light blue card.",
    )

    # Enable search indexing
    search_fields = [
        index.SearchField("text"),
        index.SearchField("url"),
    ]

    # Use PageQuerySet manager for live/draft filtering
    objects = PageQuerySet.as_manager()

    # Define panels for the admin interface
    panels = [
        FieldPanel("photo"),
        FieldPanel("url"),
        FieldPanel("text"),
        PublishingPanel(),
    ]

    def __str__(self):
        if self.text:
            return f"Fancy Card: {self.text[:50]}"
        elif self.photo:
            return f"Fancy Card: {self.photo.title}"
        else:
            return f"Fancy Card #{self.pk}"

    class Meta:
        ordering = ["text"]
        verbose_name = "Fancy Card"
        verbose_name_plural = "Fancy Cards"
