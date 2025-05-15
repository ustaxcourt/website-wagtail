from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from django.utils import timezone
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

AUTO_MANAGED_COLLECTIONS = ["Judges", "Senior Judges", "Special Trial Judges"]
RESTRICTED_ROLES = ["Chief Judge", "Chief Special Trial Judge"]


@register_snippet
class JudgeProfile(models.Model):
    first_name = models.CharField(max_length=255)
    middle_initial = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    suffix = models.CharField(max_length=3, blank=True)
    display_name = models.CharField(
        max_length=255,
        help_text="Optional full name to display (e.g., 'John A. Smith')",
        blank=True,
    )
    title = models.CharField(
        max_length=255,
        choices=[
            ("Judge", "Judge"),
            ("Senior Judge", "Senior Judge"),
            ("Special Trial Judge", "Special Trial Judge"),
        ],
    )
    chambers_telephone = models.CharField(
        max_length=20, blank=True, help_text="Chambers Telephone Number"
    )

    bio = RichTextField(blank=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("first_name"),
        FieldPanel("middle_initial"),
        FieldPanel("last_name"),
        FieldPanel("suffix"),
        FieldPanel("display_name"),
        FieldPanel("title"),
        FieldPanel("chambers_telephone"),
        FieldPanel("bio"),
    ]

    class Meta:
        ordering = ["last_name"]

    def save(self, *args, **kwargs):
        logger.info(f"Saving judge profile: {self}")
        self.last_updated_date = timezone.now()
        # Only generate a default if display_name is blank
        if not self.display_name.strip():
            parts = [self.first_name, self.middle_initial, self.last_name, self.suffix]
            # Filter out empty parts and join them with spaces
            self.display_name = " ".join(part for part in parts if part)
        super().save(*args, **kwargs)

        TARGET_COLLECTION = self.title + "s"

        OTHER_COLLECTIONS = set(AUTO_MANAGED_COLLECTIONS) - {TARGET_COLLECTION}
        # Remove the judge from all other collections
        for collection_name in OTHER_COLLECTIONS:
            try:
                collection = JudgeCollection.objects.get(name=collection_name)
                collection.ordered_judges.filter(judge=self).delete()
            except JudgeCollection.DoesNotExist:
                pass

        # Add the judge to the target collection
        try:
            collection = JudgeCollection.objects.get(name=TARGET_COLLECTION)
            # Check if the judge is already in the collection
            if not collection.ordered_judges.filter(judge=self).exists():
                JudgeCollectionOrderable.objects.create(
                    collection=collection, judge=self
                )
        except JudgeCollection.DoesNotExist:
            pass

    def __str__(self):
        return self.display_name


class JudgeCollectionOrderable(Orderable):
    """Intermediate model to make JudgeProfile orderable in JudgeCollection."""

    collection = ParentalKey(
        "JudgeCollection", related_name="ordered_judges", on_delete=models.CASCADE
    )
    judge = models.ForeignKey(
        "JudgeProfile", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("judge"),
    ]


@register_snippet
class JudgeCollection(ClusterableModel):
    """A collection of judge profiles for easy management and display."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of this collection (e.g., 'Featured Judges', 'Tax Court Judges')",
    )

    panels = [
        FieldPanel("name"),
        InlinePanel("ordered_judges", label="Judges"),
    ]

    def __str__(self):
        return self.name


@register_snippet
class JudgeRole(models.Model):
    role_name = models.CharField(
        max_length=255,
        unique=True,  # Added unique constraint to ensure no duplicate role names
        help_text="Name of the role (e.g., 'Chief Judge', 'Assistant Judge')",
    )
    judge = models.ForeignKey(
        "JudgeProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roles",
        help_text="Assign a judge to this role",
    )

    panels = [
        FieldPanel("role_name"),
        FieldPanel("judge"),
    ]

    def clean(self):
        # Restrict updates to role_name for specific roles
        if self.pk:  # Check if the object already exists
            original = JudgeRole.objects.get(pk=self.pk)
            if (
                original.role_name in RESTRICTED_ROLES
                and original.role_name != self.role_name
            ):
                raise ValidationError(
                    "You cannot modify the role name for 'Chief Judge' or 'Chief Special Trial Judge'.",
                )
        super().clean()

    def delete(self, *args, **kwargs):
        # Restrict deletion for specific roles
        if self.role_name in RESTRICTED_ROLES:
            raise ValidationError(
                "You cannot delete the role 'Chief Judge' or 'Chief Special Trial Judge'.",
            )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.role_name}, {self.judge or '** Selection Pending **'}"
