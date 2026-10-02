"""
Admin views for uploading and downloading a page's FAQ sections as CSV files.

Reached from the "FAQ CSV" button in the page editor header. See home/utils/faq_csv.py
for the CSV format and import rules.
"""

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin
from wagtail.models import Page

from home.models.custom_blocks.question_answers import QuestionAnswersBlock
from home.models.pages.enhanced_standard import EnhancedStandardPage
from home.utils.faq_csv import (
    COLUMNS,
    REQUIRED_COLUMNS,
    FAQCSVError,
    faq_section_import_csv,
    faq_section_to_csv,
    faq_sections_list,
)

MAX_UPLOAD_BYTES = 2 * 1024 * 1024


class FAQCSVUploadForm(forms.Form):
    section_id = forms.CharField(required=False, widget=forms.HiddenInput)
    csv_file = forms.FileField(label="CSV file")
    display_filter_section = forms.BooleanField(
        required=False,
        label="Display Filter Section",
        help_text="Only used when adding a new FAQ section.",
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Upload a .csv file.")
        if csv_file.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError("The file is larger than 2 MB.")
        return csv_file


def _get_editable_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    if not issubclass(page.specific_class, EnhancedStandardPage):
        raise Http404("This page type does not support FAQ sections.")
    if not page.permissions_for_user(request.user).can_edit():
        raise PermissionDenied
    return page.specific


def _section_summary(index, section):
    value = QuestionAnswersBlock().to_python(section["value"])
    questions = value["questions"]
    return {
        "id": section["id"],
        "number": index,
        "count": len(questions),
        "first_question": questions[0]["question"] if questions else "",
        "display_filter_section": value["display_filter_section"],
    }


class FAQCSVView(WagtailAdminTemplateMixin, TemplateView):
    template_name = "wagtailadmin/faq_csv/index.html"
    page_title = "FAQ CSV import/export"
    header_icon = "table"

    def dispatch(self, request, page_id):
        self.page = _get_editable_page(request, page_id)
        return super().dispatch(request, page_id)

    def get_breadcrumbs_items(self):
        return self.breadcrumbs_items + [
            {
                "url": reverse("wagtailadmin_pages:edit", args=[self.page.pk]),
                "label": self.page.get_admin_display_title(),
            },
            {"label": self.page_title},
        ]

    def get_context_data(self, **kwargs):
        latest = self.page.get_latest_revision_as_object()
        lock = self.page.get_lock()
        return super().get_context_data(
            page=self.page,
            sections=[
                _section_summary(i, s)
                for i, s in enumerate(faq_sections_list(latest), start=1)
            ],
            columns=COLUMNS,
            required_columns=REQUIRED_COLUMNS,
            lock_message=lock.get_message(self.request.user)
            if lock and lock.for_user(self.request.user)
            else None,
            **kwargs,
        )

    def post(self, request, page_id):
        lock = self.page.get_lock()
        if lock and lock.for_user(request.user):
            raise PermissionDenied

        form = FAQCSVUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            errors = [e for field in form.errors.values() for e in field]
            return self.render_errors(errors)

        section_id = form.cleaned_data["section_id"] or None
        try:
            faq_section_import_csv(
                request=request,
                page=self.page,
                data=form.cleaned_data["csv_file"].read(),
                section_id=section_id,
                display_filter_section=form.cleaned_data["display_filter_section"],
            )
        except FAQCSVError as e:
            return self.render_errors(e.errors)

        messages.success(
            request,
            "FAQ section "
            + ("replaced" if section_id else "added")
            + " from CSV and saved as a draft. Review it, then publish or submit for moderation.",
        )
        return redirect("wagtailadmin_pages:edit", self.page.pk)

    def render_errors(self, errors):
        context = self.get_context_data(import_errors=errors)
        return self.render_to_response(context, status=400)


def faq_csv_download(request, page_id, section_id):
    page = _get_editable_page(request, page_id)
    latest = page.get_latest_revision_as_object()
    sections = faq_sections_list(latest)
    section = next((s for s in sections if s.get("id") == section_id), None)
    if section is None:
        raise Http404("FAQ section not found.")

    filename = f"{page.slug}-faq"
    if len(sections) > 1:
        filename += f"-{sections.index(section) + 1}"
    # The byte order mark makes Excel read the file as UTF-8
    response = HttpResponse(
        faq_section_to_csv(section).encode("utf-8-sig"),
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response
