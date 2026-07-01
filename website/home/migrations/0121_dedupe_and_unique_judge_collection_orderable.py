"""
0121: Remove duplicate JudgeCollectionOrderable rows and enforce a unique
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
            f"0121: deduped collection={dup['collection_id']} "
            f"judge={dup['judge_id']} (removed {n})"
        )

    logger.info(f"0121: total duplicate orderables removed: {total_removed}")


def noop(apps, schema_editor):
    pass


def add_unique_constraint_if_not_exists(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        # Check by columns rather than constraint name so this is safe even if
        # the constraint was created manually under a different name.
        schema_editor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_index i
                    JOIN pg_class t ON t.oid = i.indrelid
                    WHERE t.relname = 'home_judgecollectionorderable'
                      AND i.indisunique
                      AND (
                          SELECT array_agg(a.attname ORDER BY a.attname)
                          FROM pg_attribute a
                          WHERE a.attrelid = i.indrelid
                            AND a.attnum = ANY(i.indkey)
                      ) = ARRAY['collection_id', 'judge_id']
                ) THEN
                    ALTER TABLE home_judgecollectionorderable
                    ADD CONSTRAINT home_judgecollectionorde_collection_id_judge_id_c8fb48d9_uniq
                    UNIQUE (collection_id, judge_id);
                END IF;
            END $$;
        """)
    elif vendor == "sqlite3":
        # CREATE UNIQUE INDEX IF NOT EXISTS is cross-version safe on SQLite.
        schema_editor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS"
            ' "home_judgecollectionorde_collection_id_judge_id_c8fb48d9_uniq"'
            ' ON "home_judgecollectionorderable" ("collection_id", "judge_id")'
        )
    else:
        raise NotImplementedError(f"Unsupported database vendor: {vendor}")


def drop_unique_constraint(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute(
            "ALTER TABLE home_judgecollectionorderable"
            " DROP CONSTRAINT IF EXISTS"
            " home_judgecollectionorde_collection_id_judge_id_c8fb48d9_uniq"
        )
    elif vendor == "sqlite3":
        schema_editor.execute(
            "DROP INDEX IF EXISTS"
            ' "home_judgecollectionorde_collection_id_judge_id_c8fb48d9_uniq"'
        )
    else:
        raise NotImplementedError(f"Unsupported database vendor: {vendor}")


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0120_seed_judge_index_bottom_tiles"),
    ]

    operations = [
        migrations.RunPython(dedupe_orderables, noop),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    add_unique_constraint_if_not_exists,
                    drop_unique_constraint,
                ),
            ],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="judgecollectionorderable",
                    unique_together={("collection", "judge")},
                ),
            ],
        ),
    ]
