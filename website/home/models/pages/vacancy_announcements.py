from django.db import models
from wagtail.models import Page, ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from django.core.exceptions import ValidationError
from wagtail.documents.models import Document
from wagtail.models import Orderable

from datetime import date
from home.models.pages.standard import StandardPage


class VacancyAnnouncementsPage(StandardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        today = date.today()
        active_vacancies = VacancyEntry.objects.filter(
            parentpage=self, closing_date__gte=today
        ).order_by("closing_date")
        context["active_vacancies"] = active_vacancies
        return context

    content_panels = Page.content_panels + [
        InlinePanel("vacancies", label="Vacancies"),
    ]


class VacancyEntry(Orderable):
    parentpage = ParentalKey(
        "VacancyAnnouncementsPage", related_name="vacancies", on_delete=models.CASCADE
    )

    number = models.CharField(max_length=50, help_text="Vacancy announcement number")
    position_title = models.CharField(
        max_length=255, help_text="Position title, series, and grade"
    )
    closing_date = models.DateField(
        help_text="Closing date for the vacancy", blank=True, null=True
    )
    closing_date_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="Until the position is filled",
        help_text='Text for closing date display, e.g., "June 30, 2025 or until filled"',
    )

    url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Link to the vacancy announcement",
    )

    attachment = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Upload a PDF or Word doc of the vacancy (optional)",
    )

    panels = [
        FieldPanel("number"),
        FieldPanel("position_title"),
        FieldPanel("closing_date"),
        FieldPanel("closing_date_text"),
        FieldPanel("url"),
        FieldPanel("attachment"),
    ]

    def clean(self):
        super().clean()
        # Check if closing_date is before today
        if self.closing_date and self.closing_date < date.today():
            raise ValidationError(
                {"closing_date": "Closing date cannot be in the past."}
            )
        # Ensure at least one of url or attachment is provided
        if not self.url and not self.attachment:
            raise ValidationError(
                "Please provide either a URL or an attachment for the vacancy."
            )

    class Meta:
        ordering = ["closing_date"]

    def is_active(self):
        return self.closing_date >= date.today()
