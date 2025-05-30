from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet


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
