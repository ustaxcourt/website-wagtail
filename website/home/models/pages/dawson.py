from home.models.pages.standard import StandardPage
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import ParentalKey
from django.db import models
from modelcluster.models import ClusterableModel


# Card models have been moved to home.models.snippets.cards
# These inline models remain for page-specific relationships


class DawsonSimpleCard(models.Model):
    """Inline model to link SimpleCard snippets to DawsonPage."""

    parent_page = ParentalKey(
        "DawsonPage", related_name="simple_cards", on_delete=models.CASCADE
    )
    simple_card = models.ForeignKey(
        "home.SimpleCard", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("simple_card"),
    ]

    def __str__(self):
        return f"Simple Card on {self.parent_page.title}: {self.simple_card}"


class DawsonFancyCard(models.Model):
    """Inline model to link FancyCard snippets to DawsonPage."""

    parent_page = ParentalKey(
        "DawsonPage", related_name="fancy_cards", on_delete=models.CASCADE
    )
    fancy_card = models.ForeignKey(
        "home.FancyCard", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("fancy_card"),
    ]

    def __str__(self):
        return f"Fancy Card on {self.parent_page.title}: {self.fancy_card}"


class SimpleCardGroup(ClusterableModel):
    """Group model for dynamically grouping Simple Cards."""

    parent_page = ParentalKey(
        "DawsonPage", related_name="card_groups", on_delete=models.CASCADE
    )

    group_label = models.CharField(
        blank=True,
        max_length=255,
        help_text="Label for this group of cards (e.g., 'Section 1: Featured Cards').",
    )

    panels = [
        FieldPanel("group_label"),
        InlinePanel("group_cards", label="Cards in this Group"),
    ]

    def __str__(self):
        return (
            self.group_label
            if self.group_label
            else f"Simple Card Group - {self.parent_page.title}"
        )


class SimpleCardGroupItem(models.Model):
    """Individual card item in a SimpleCardGroup."""

    group = ParentalKey(
        "SimpleCardGroup", related_name="group_cards", on_delete=models.CASCADE
    )
    simple_card = models.ForeignKey(
        "home.SimpleCard", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("simple_card"),
    ]

    def __str__(self):
        return f"Card in {self.group}: {self.simple_card}"


class PhotoDedication(models.Model):
    """Model to store data for a dedication."""

    dawson_page = ParentalKey(
        "DawsonPage",
        related_name="photo_dedication",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    enhanced_standard_page = ParentalKey(
        "EnhancedStandardPage",
        related_name="photo_dedications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255,
        help_text="Enter the title for the dedication",
    )

    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image to display with this dedication",
    )

    paragraph_text = RichTextField(
        blank=True,
        help_text="Add the main paragraph text for the dedication section",
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Enter alternative text for the image",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("photo"),
        FieldPanel("paragraph_text"),
    ]


class Meta:
    verbose_name = "Photo Dedication"
    verbose_name_plural = "Photo Dedication"


class DawsonPage(StandardPage):
    """Page model for Dawson eFiling Page."""

    content_panels = StandardPage.content_panels + [
        InlinePanel("fancy_cards", label="Fancy Card Sections"),
        InlinePanel("simple_cards", label="Simple Card Sections"),
        InlinePanel("card_groups", label="Card Group Sections"),
        InlinePanel("photo_dedication", label="Photo Dedication"),
    ]
