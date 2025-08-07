from django.db import models
from wagtail.models import WorkflowState
from django.core.exceptions import (
    ValidationError,
)  # Import ValidationError for clean method


class CustomWorkflowState(WorkflowState):
    review_by_date = models.DateTimeField(
        null=False, blank=False, verbose_name="Publish Deadline"
    )
    publish_deadline = models.DateTimeField(
        null=False,
        blank=False,
        help_text="Required date/time when this item should be published by.",
    )

    note = models.TextField(null=True, blank=True, verbose_name="Editor/Moderator Note")
    note = models.TextField(null=True, blank=True)

    class Meta:
        abstract = False  # This ensures a table is created for CustomWorkflowState

    def clean(self):
        super().clean()
        if self.publish_deadline and self.review_by_date:
            if self.publish_deadline < self.review_by_date:
                raise ValidationError(
                    "Publish deadline cannot be earlier than the review by date."
                )
