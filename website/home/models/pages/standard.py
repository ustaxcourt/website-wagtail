from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class StandardPage(Page):
    class Meta:
        abstract = False

    body = RichTextField(blank=True, help_text="Insert text here.")

    content_panels = Page.content_panels + [FieldPanel("body")]
