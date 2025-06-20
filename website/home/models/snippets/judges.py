from django.db import models, transaction
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from django.utils import timezone
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from django.core.exceptions import ValidationError
from wagtail.search import index


import logging

logger = logging.getLogger(__name__)

AUTO_MANAGED_COLLECTIONS = ["Judges", "Senior Judges", "Special Trial Judges"]
RESTRICTED_ROLES = ["Chief Judge", "Chief Special Trial Judge"]


@register_snippet
class JudgeProfile(index.Indexed, models.Model):
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

    search_fields = [
        index.SearchField("last_name", partial_match=True),
        index.AutocompleteField("last_name"),
        index.SearchField("first_name", partial_match=True),
        index.AutocompleteField("first_name"),
    ]

    class Meta:
        ordering = ["last_name"]

    def save(self, *args, **kwargs):
        logger.info(f"Saving judge profile: {self}")
        self.last_updated_date = timezone.now()
        if not self.display_name.strip():
            parts = [self.first_name, self.middle_initial, self.last_name, self.suffix]
            self.display_name = " ".join(part for part in parts if part)

        # Determine current collection before super().save() in case title changes
        try:
            if self.pk:
                old_self = JudgeProfile.objects.get(pk=self.pk)
                old_target_collection_name = old_self.title + "s"
            else:
                old_target_collection_name = None
        except JudgeProfile.DoesNotExist:
            old_target_collection_name = None

        super().save(*args, **kwargs)  # Save the judge profile first

        current_target_collection_name = self.title + "s"

        collections_to_update = set()

        # Remove from old collection if title changed and it was an auto-managed one
        if (
            old_target_collection_name
            and old_target_collection_name != current_target_collection_name
        ):
            if old_target_collection_name in AUTO_MANAGED_COLLECTIONS:
                try:
                    collection = JudgeCollection.objects.get(
                        name=old_target_collection_name
                    )
                    if collection.ordered_judges.filter(judge=self).exists():
                        logger.info(
                            f"Removing judge {self} from old collection {collection.name}"
                        )
                        collection.ordered_judges.filter(judge=self).delete()
                        collections_to_update.add(collection)
                except JudgeCollection.DoesNotExist:
                    logger.warning(
                        f"Old target collection {old_target_collection_name} not found."
                    )
                    pass

        # Add/Update in the current target collection if it's an auto-managed one
        if current_target_collection_name in AUTO_MANAGED_COLLECTIONS:
            try:
                collection, created = JudgeCollection.objects.get_or_create(
                    name=current_target_collection_name
                )
                if not collection.ordered_judges.filter(judge=self).exists():
                    logger.info(f"Adding judge {self} to collection {collection.name}")
                    JudgeCollectionOrderable.objects.create(
                        collection=collection, judge=self
                    )
                collections_to_update.add(collection)
            except JudgeCollection.DoesNotExist:  # Should be handled by get_or_create
                logger.error(
                    f"Target collection {current_target_collection_name} could not be fetched or created."
                )
                pass

        # Explicitly save collections that were modified to trigger their reordering logic
        for collection_to_save in collections_to_update:
            collection_to_save.save()

    def __str__(self):
        return self.display_name


class JudgeCollectionOrderable(Orderable):
    collection = ParentalKey(
        "JudgeCollection", related_name="ordered_judges", on_delete=models.CASCADE
    )
    judge = models.ForeignKey(
        "JudgeProfile",
        on_delete=models.CASCADE,
        related_name="collection_orderables",  # Changed related_name
    )

    panels = [
        FieldPanel("judge"),
    ]

    class Meta(Orderable.Meta):  # Ensure Meta from Orderable is inherited
        pass


@register_snippet
class JudgeCollection(ClusterableModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of this collection (e.g., 'Featured Judges', 'Tax Court Judges')",
    )

    panels = [
        FieldPanel("name"),
        InlinePanel("ordered_judges", label="Judges"),
    ]

    def _reorder_judges(self):
        """
        Reorders judges within this collection.
        Judges with a RESTRICTED_ROLE are placed first.
        Other judges are sorted by last_name, then first_name.
        """
        logger.info(f"Reordering judges for collection: {self.name}")

        # Get all JudgeCollectionOrderable instances related to this collection
        # Ensure we are working with objects that have judge profiles preloaded to avoid N+1 queries
        judge_orderables = list(self.ordered_judges.select_related("judge").all())
        if not judge_orderables:
            logger.info(f"No judges to reorder in collection: {self.name}")
            return

        restricted_judge_orderable = None
        other_judge_orderables = []

        # Identify the judge with a restricted role, if any
        # We check the JudgeRole model for any judge in this collection's orderables
        # This assumes a judge can only have one role or the first restricted role found is prioritized.
        # If multiple judges could have restricted roles in the same collection, refinement is needed.

        # Get all judge_ids in this collection
        judge_ids_in_collection = [jo.judge.id for jo in judge_orderables]

        # Find which of these judges have a restricted role
        restricted_judges_in_collection = (
            JudgeProfile.objects.filter(
                id__in=judge_ids_in_collection, roles__role_name__in=RESTRICTED_ROLES
            ).distinct()
        )  # Use distinct if a judge could somehow match multiple restricted roles

        # For simplicity, we take the first restricted judge found.
        # If there's a specific one (e.g. only "Chief Judge" matters for being first), filter further.
        prioritized_judge_profile = restricted_judges_in_collection.first()

        if prioritized_judge_profile:
            logger.info(
                f"Prioritized judge found: {prioritized_judge_profile} in collection {self.name}"
            )
            for jo in judge_orderables:
                if jo.judge_id == prioritized_judge_profile.id:
                    restricted_judge_orderable = jo
                else:
                    other_judge_orderables.append(jo)
        else:
            logger.info(f"No prioritized judge in collection: {self.name}")
            other_judge_orderables = list(judge_orderables)  # Make a mutable copy

        # Sort other judges by last name, then first name (as per JudgeProfile.Meta.ordering)
        other_judge_orderables.sort(
            key=lambda jo: (jo.judge.last_name.lower(), jo.judge.first_name.lower())
        )

        # Combine the lists
        final_ordered_list = []
        if restricted_judge_orderable:
            final_ordered_list.append(restricted_judge_orderable)
        final_ordered_list.extend(other_judge_orderables)

        # Update the sort_order field for each JudgeCollectionOrderable
        # This needs to be done carefully to avoid issues with modelcluster's order management.
        # The most straightforward way is to update the sort_order directly.
        with transaction.atomic():  # Ensure all updates are done or none
            for i, judge_orderable_item in enumerate(final_ordered_list):
                if judge_orderable_item.sort_order != i:
                    judge_orderable_item.sort_order = i
                    # Only save if pk exists (it should) and sort_order changed
                    if judge_orderable_item.pk:
                        # Only update the sort_order field to be efficient
                        judge_orderable_item.save(update_fields=["sort_order"])
                        logger.debug(
                            f"Set sort_order={i} for {judge_orderable_item.judge} in {self.name}"
                        )
        logger.info(f"Finished reordering judges for collection: {self.name}")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Always reorder after any save, whether it's creation or update.
        # This handles manual reordering in admin, programmatic changes, etc.
        self._reorder_judges()

    def __str__(self):
        return self.name


@register_snippet
class JudgeRole(models.Model):
    role_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the role (e.g., 'Chief Judge', 'Assistant Judge')",
    )
    judge = models.ForeignKey(
        "JudgeProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roles",  # This allows JudgeProfile.roles to get all roles of a judge
        help_text="Assign a judge to this role",
    )

    panels = [
        FieldPanel("role_name"),
        FieldPanel("judge"),
    ]

    def clean(self):
        if self.pk:
            original = JudgeRole.objects.get(pk=self.pk)
            if (
                original.role_name in RESTRICTED_ROLES
                and original.role_name != self.role_name
            ):
                raise ValidationError(
                    "You cannot modify the role name for 'Chief Judge' or 'Chief Special Trial Judge'."
                )
        # Ensure a judge is not assigned the same restricted role multiple times
        # (though unique=True on role_name prevents duplicate role names entirely)
        # More relevant: Ensure a judge isn't assigned multiple *different* restricted roles if that's not allowed
        if self.judge and self.role_name in RESTRICTED_ROLES:
            existing_restricted_roles_for_judge = JudgeRole.objects.filter(
                judge=self.judge, role_name__in=RESTRICTED_ROLES
            ).exclude(pk=self.pk)  # Exclude self if updating
            if existing_restricted_roles_for_judge.exists():
                raise ValidationError(
                    f"Judge {self.judge} is already assigned another restricted role."
                )
        super().clean()

    def delete(self, *args, **kwargs):
        if self.role_name in RESTRICTED_ROLES:
            raise ValidationError(
                "You cannot delete the role 'Chief Judge' or 'Chief Special Trial Judge'."
            )
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # When a role is saved, especially if a judge is assigned/unassigned
        # from a restricted role, the collections they belong to might need reordering.
        super().save(*args, **kwargs)

        collections_to_resort = set()
        if self.judge:  # If a judge is associated with this role
            # Find all collections this judge is part of through JudgeCollectionOrderable
            for orderable in self.judge.collection_orderables.select_related(
                "collection"
            ).all():
                collections_to_resort.add(orderable.collection)

        # If this role was previously assigned to a different judge (or no judge)
        # and that judge is different from the current one, their collections might also need reordering.
        if self.pk:
            try:
                old_instance = JudgeRole.objects.get(pk=self.pk)
                if old_instance.judge and old_instance.judge != self.judge:
                    for (
                        orderable
                    ) in old_instance.judge.collection_orderables.select_related(
                        "collection"
                    ).all():
                        collections_to_resort.add(orderable.collection)
            except JudgeRole.DoesNotExist:
                pass  # Should not happen if self.pk exists

        for collection in collections_to_resort:
            if (
                collection.name in AUTO_MANAGED_COLLECTIONS
            ):  # Or apply to all collections if needed
                logger.info(
                    f"Triggering reorder for collection {collection.name} due to JudgeRole save."
                )
                collection.save()  # This will call _reorder_judges

    def __str__(self):
        return f"{self.role_name}, {self.judge or '** Selection Pending **'}"
