from django.db import models
from wagtail.models import Page, ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from django.core.exceptions import ValidationError
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
    closing_date = models.DateField(help_text="Closing date for the vacancy")
    url = models.URLField(max_length=255, help_text="Link to the vacancy announcement")

    panels = [
        FieldPanel("number"),
        FieldPanel("position_title"),
        FieldPanel("closing_date"),
        FieldPanel("url"),
    ]

    def clean(self):
        super().clean()
        # Check if closing_date is before today
        if self.closing_date and self.closing_date < date.today():
            raise ValidationError(
                {"closing_date": "Closing date cannot be in the past."}
            )

    class Meta:
        ordering = ["closing_date"]

    def is_active(self):
        return self.closing_date >= date.today()
