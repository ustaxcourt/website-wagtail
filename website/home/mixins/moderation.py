from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.admin.widgets import AdminDateTimeInput
from django.utils.dateparse import parse_datetime


class ModerationMixin(models.Model):
    """
    Mixin to add moderation fields including a Review by date/time.
    Key behavior:
    - The field is OPTIONAL during normal edits/autosaves.
    - The field is REQUIRED only during Submit-for-Moderation (caller sets _require_review_by=True).
    - Preview operations skip validation.
    - After submission (when you copy the value to WorkflowState and clear it),
      you should save with clean=False to avoid re-validating.
    """

    _require_review_by: bool = False
    _skip_review_by_validation: bool = False

    review_by = models.DateTimeField(
        null=True,
        blank=True,  # allow blank at model level; we enforce conditionally
        help_text="Deadline for review and moderation of this content.",
        verbose_name="Review by date",
    )

    note = models.TextField(
        null=True,
        blank=True,
        help_text="Optional note for moderators when submitting content for review.",
        verbose_name="Moderation note",
    )

    class Meta:
        abstract = True

    def save_revision(self, *args, **kwargs):
        """
        Allow callers to pass clean=False (e.g., after we clear review_by post-submit).
        We also back-propagate the 'review_by' value from the revision's serialized content
        to the live model field (simple consistency).
        """
        clean = kwargs.pop("clean", True)
        revision = super().save_revision(*args, clean=clean, **kwargs)

        if hasattr(self, "review_by") and revision:
            review_by_from_revision = revision.content.get("review_by")
            if review_by_from_revision:
                self.review_by = (
                    parse_datetime(review_by_from_revision)
                    if isinstance(review_by_from_revision, str)
                    else review_by_from_revision
                )
                # Direct model save; Django's save() doesn't call full_clean
                super().save(update_fields=["review_by"])
            else:
                self.review_by = None
                super().save(update_fields=["review_by"])
        return revision

    def on_workflow_cancelled(self):
        """When workflow is cancelled - clear the review_by date."""
        if hasattr(self, "review_by"):
            self.review_by = None
            self.save(update_fields=["review_by"])

    def on_workflow_approved(self):
        """When workflow is approved - clear the review_by date."""
        if hasattr(self, "review_by"):
            self.review_by = None
            self.save(update_fields=["review_by"])

    def get_latest_revision_as_object(self):
        """
        Ensure review_by is loaded from the latest revision for preview.
        Set skip flag to avoid validation during preview object creation.
        """
        obj = super().get_latest_revision_as_object()
        obj._skip_review_by_validation = True

        if (
            hasattr(obj, "review_by")
            and hasattr(self, "revisions")
            and self.revisions.exists()
        ):
            try:
                latest_revision = self.revisions.latest("created_at")
                revision_review_by = latest_revision.content.get("review_by")
                if revision_review_by:
                    obj.review_by = (
                        parse_datetime(revision_review_by)
                        if isinstance(revision_review_by, str)
                        else revision_review_by
                    )
                else:
                    obj.review_by = getattr(self, "review_by", None)
            except Exception:
                obj.review_by = getattr(self, "review_by", None)

        return obj

    @classmethod
    def get_moderation_panels(cls):
        """Panels for the Moderation tab."""
        return [
            FieldPanel(
                "review_by",
                widget=AdminDateTimeInput(),
                help_text="Target date/time for moderators to complete review.",
            ),
            FieldPanel(
                "note",
                help_text="Optional note for moderators when submitting content for review.",
            ),
        ]

    @property
    def is_review_overdue(self) -> bool:
        """True if review_by is set and <= now()."""
        if not self.review_by:
            return False
        review_by_aware = (
            timezone.make_aware(self.review_by)
            if timezone.is_naive(self.review_by)
            else self.review_by
        )
        return review_by_aware <= timezone.now()

    @property
    def days_until_review(self):
        """Days until review_by (negative if overdue)."""
        if not self.review_by:
            return None
        review_by_aware = (
            timezone.make_aware(self.review_by)
            if timezone.is_naive(self.review_by)
            else self.review_by
        )
        delta = review_by_aware - timezone.now()
        return delta.days
