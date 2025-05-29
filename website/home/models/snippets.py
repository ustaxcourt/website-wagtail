from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet
from home.models.config import IconCategories


class NavigationRibbonLink(models.Model):
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=200, choices=IconCategories.choices)
    url = models.CharField(max_length=1000)

    navigation_ribbon = ParentalKey(
        "NavigationRibbon", related_name="links", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("icon"),
        FieldPanel("url"),
    ]


@register_snippet
class NavigationRibbon(ClusterableModel):
    name = models.CharField(max_length=255)

    panels = [
        InlinePanel("links", label="Links"),  # Now properly references the ParentalKey
    ]

    def __str__(self):
        return self.name


@register_snippet
class CommonText(models.Model):
    name = models.CharField(
        max_length=255, help_text="Name of the text snippet", blank=False
    )
    text = RichTextField(help_text="HTML Rich text content", blank=False)

    panels = [
        FieldPanel("name"),
        FieldPanel("text"),
    ]

    def __str__(self):
        return self.name
