from wagtail.admin.forms import WagtailAdminPageForm, WagtailAdminModelForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings


class ReviewByRequiredOnSubmitForm(WagtailAdminPageForm):
    def _is_submit_for_moderation(self) -> bool:
        return any(k.startswith("action-submit") for k in self.data.keys())

    def clean(self):
        cleaned = super().clean()
        if self._is_submit_for_moderation():
            review_by = cleaned.get("review_by")
            if not review_by:
                self.add_error(
                    "review_by",
                    ValidationError(
                        "Please set a Review by date before submitting to moderation."
                    ),
                )
            else:
                aware = (
                    timezone.make_aware(review_by)
                    if timezone.is_naive(review_by)
                    else review_by
                )
                if aware <= timezone.now():
                    self.add_error(
                        "review_by",
                        ValidationError(
                            "Review by date and time cannot be in the past."
                        ),
                    )
        return cleaned


class ReviewByRequiredOnSubmitSnippetForm(WagtailAdminModelForm):
    """
    Require 'review_by' only when submitting a SNIPPET for moderation.
    Covers a variety of button/param names used by Wagtail/custom UIs.
    """

    def _is_submit_for_moderation(self) -> bool:
        d = self.data
        keys = list(d.keys())

        # Optional debug: shows you exactly what the form is receiving
        if getattr(settings, "DEBUG", False):
            try:
                print("Snippet POST keys:", keys)
                print(
                    "Snippet POST action-* values:",
                    {k: d.get(k) for k in keys if k.startswith("action-")},
                )
                print("Snippet POST 'action':", d.get("action"))
                print("Snippet POST 'transition':", d.get("transition"))
                print("Snippet POST 'workflow-action':", d.get("workflow-action"))
            except Exception:
                pass

        # Classic action-submit* buttons
        if any(k.startswith("action-submit") for k in keys):
            return True

        # Plain 'action' param
        action_val = (d.get("action") or "").lower()
        if action_val in {"submit", "submit_for_moderation", "workflow-submit"}:
            return True

        # action-* controls where value indicates submit
        for k in keys:
            if k.startswith("action-"):
                val = (d.get(k) or "").lower()
                if val.startswith("submit") or val == "submit_for_moderation":
                    return True

        # Workflow params used by some templates
        if (d.get("workflow-action") or "").lower() == "submit":
            return True
        if "submit" in (d.get("transition") or "").lower():
            return True

        # Legacy hidden input
        if "submit_for_moderation" in keys:
            return True

        return False

    def clean(self):
        cleaned = super().clean()
        if self._is_submit_for_moderation():
            review_by = cleaned.get("review_by")
            if not review_by:
                self.add_error(
                    "review_by",
                    ValidationError(
                        "Please set a Review by date before submitting to moderation."
                    ),
                )
            else:
                aware = (
                    timezone.make_aware(review_by)
                    if timezone.is_naive(review_by)
                    else review_by
                )
                if aware <= timezone.now():
                    self.add_error(
                        "review_by",
                        ValidationError(
                            "Review by date and time cannot be in the past."
                        ),
                    )
        return cleaned
