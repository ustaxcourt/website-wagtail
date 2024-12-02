from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

class TestPage(Page):
    body = RichTextField(blank=True)
    other = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('other'),
        FieldPanel('body'),
    ]