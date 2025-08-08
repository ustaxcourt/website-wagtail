from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.admin.widgets import AdminDateTimeInput


class ModerationMixin(models.Model):
    """
    Mixin to add moderation fields including a review by date and time.
    Should be used with WorkflowMixin, DraftStateMixin, RevisionMixin.
    """

    review_by = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional deadline for review and moderation of this content.",
    )

    class Meta:
        abstract = True

    def clean(self):
        """Validate that review_by datetime is not in the past."""
        super().clean()
        if self.review_by:
            # Make the review_by timezone-aware if it's naive
            review_by_aware = self.review_by
            if timezone.is_naive(review_by_aware):
                review_by_aware = timezone.make_aware(review_by_aware)

            # Always validate that review_by is not in the past
            # (regardless of live status - this prevents setting invalid dates)
            if review_by_aware <= timezone.now():
                raise ValidationError(
                    {"review_by": "Review by date and time cannot be in the past."}
                )

    @classmethod
    def get_moderation_panels(cls):
        """Return the moderation panels for the admin interface."""
        return [
            FieldPanel("review_by", widget=AdminDateTimeInput()),
        ]

    @property
    def is_review_overdue(self):
        """Check if the review datetime has passed."""
        if not self.review_by:
            return False

        # Make timezone-aware comparison
        review_by_aware = self.review_by
        if timezone.is_naive(review_by_aware):
            review_by_aware = timezone.make_aware(review_by_aware)

        # Check if review date has passed
        is_overdue = review_by_aware <= timezone.now()

        # For pages, also check if there's an active workflow
        if hasattr(self, "workflow_in_progress"):
            # If there's an active workflow, show overdue status regardless of live status
            if self.workflow_in_progress:
                return is_overdue

        # For non-live content (drafts), always show overdue status
        if hasattr(self, "live") and not self.live:
            return is_overdue

        # For live content with no active workflow, still show overdue if there's a review date
        # (this helps with content that needs periodic review)
        return is_overdue

    @property
    def days_until_review(self):
        """Calculate days until review datetime (negative if overdue)."""
        if not self.review_by:
            return None

        # Make timezone-aware comparison
        review_by_aware = self.review_by
        if timezone.is_naive(review_by_aware):
            review_by_aware = timezone.make_aware(review_by_aware)

        now = timezone.now()
        delta = review_by_aware - now
        return delta.days
