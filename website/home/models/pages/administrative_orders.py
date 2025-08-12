from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable, ParentalKey
from home.models.custom_blocks.common import custom_promote_panels
from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitForm


from home.models.pages.standard import StandardPage


class PDFs(Orderable):
    page = ParentalKey(
        "AdministrativeOrdersPage", related_name="pdfs", on_delete=models.CASCADE
    )

    pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("pdf"),
    ]


class AdministrativeOrdersPage(StandardPage):
    base_form_class = ReviewByRequiredOnSubmitForm

    content_panels = StandardPage.content_panels + [
        InlinePanel("pdfs", label="PDFs"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )
