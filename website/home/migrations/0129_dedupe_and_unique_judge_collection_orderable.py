"""
0129: Remove duplicate JudgeCollectionOrderable rows and enforce a unique
constraint on (collection, judge) so the admin InlinePanel can no longer save
two rows for the same judge in the same collection.

Sandbox had `Ronald L. Buch` listed twice in the `Judges` collection because the
InlinePanel doesn't enforce uniqueness on its own; this migration cleans that up
(keeps the orderable with the lowest sort_order, deletes the rest) before adding
the schema-level constraint.
"""

from django.db import migrations, models


def dedupe_orderables(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)

    Orderable = apps.get_model("home", "JudgeCollectionOrderable")

    # Group by (collection_id, judge_id) and find groups with more than one row.
    duplicates = (
        Orderable.objects.values("collection_id", "judge_id")
        .annotate(count=models.Count("id"))
        .filter(count__gt=1)
    )

    total_removed = 0
    for dup in duplicates:
        # Keep the row with the lowest sort_order (the visible-first one) and
        # drop the rest.
        rows = Orderable.objects.filter(
            collection_id=dup["collection_id"], judge_id=dup["judge_id"]
        ).order_by("sort_order", "id")
        keep = rows.first()
        extras = rows.exclude(pk=keep.pk)
        n = extras.count()
        extras.delete()
        total_removed += n
        logger.info(
            f"0129: deduped collection={dup['collection_id']} "
            f"judge={dup['judge_id']} (removed {n})"
        )

    logger.info(f"0129: total duplicate orderables removed: {total_removed}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0128_reseed_bottom_tiles_after_admin_edits"),
    ]

    operations = [
        migrations.RunPython(dedupe_orderables, noop),
        migrations.AlterUniqueTogether(
            name="judgecollectionorderable",
            unique_together={("collection", "judge")},
        ),
    ]
