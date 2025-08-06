from django.db import models
from wagtail.admin.panels import FieldPanel


class PublishDeadlineMixin(models.Model):
    review_by_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Publish Deadline2",
        help_text="item should be reviewed by.",
    )
    publish_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional deadline for publishing this content.",
    )

    class Meta:
        abstract = True

    publish_deadline_panels = [
        FieldPanel("publish_deadline"),
        FieldPanel("review_by_date"),
    ]
