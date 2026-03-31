"""Data migration: convert photo_dedication photo field from ImageBlock format
({'image': <id>, 'alt_text': '...', 'decorative': False}) to ImageChooserBlock
format (just the image ID integer). Also copies alt_text from the old ImageBlock
into the block-level alt_text field if it was empty."""

import json

from django.db import migrations


def convert_photo_dedication_data(apps, schema_editor):
    """Use raw SQL to avoid StreamField deserialization issues in migrations."""
    connection = schema_editor.connection
    cursor = connection.cursor()

    cursor.execute("SELECT page_ptr_id, body FROM home_enhancedstandardpage")
    rows = cursor.fetchall()

    for page_id, body_raw in rows:
        if not body_raw:
            continue

        # PostgreSQL jsonb returns already-parsed Python objects;
        # SQLite returns a JSON string
        body_data = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

        if not isinstance(body_data, list):
            continue

        changed = False
        for block in body_data:
            if block.get("type") != "photo_dedication":
                continue

            value = block.get("value", {})
            photo = value.get("photo")

            if isinstance(photo, dict):
                image_id = photo.get("image")
                old_alt = photo.get("alt_text", "")

                value["photo"] = image_id
                changed = True

                if not value.get("alt_text") and old_alt:
                    value["alt_text"] = old_alt

        if changed:
            cursor.execute(
                "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                [json.dumps(body_data), page_id],
            )


def reverse_migration(apps, schema_editor):
    """No-op reverse: we can't reconstruct the decorative flag."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0104_reverse_pamphletentry_sort_order"),
    ]

    operations = [
        migrations.RunPython(convert_photo_dedication_data, reverse_migration),
    ]
