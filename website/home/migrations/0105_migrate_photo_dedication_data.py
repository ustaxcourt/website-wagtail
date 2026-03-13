"""Data migration: convert photo_dedication photo field from ImageBlock format
({'image': <id>, 'alt_text': '...', 'decorative': False}) to ImageChooserBlock
format (just the image ID integer). Also copies alt_text from the old ImageBlock
into the block-level alt_text field if it was empty."""

import json

from django.db import migrations


def convert_photo_dedication_data(apps, schema_editor):
    EnhancedStandardPage = apps.get_model("home", "EnhancedStandardPage")
    for page in EnhancedStandardPage.objects.all():
        if not page.body:
            continue

        body_data = json.loads(
            page.body.raw_data if hasattr(page.body, "raw_data") else page.body
        )

        if not isinstance(body_data, list):
            continue

        changed = False
        for block in body_data:
            if block.get("type") != "photo_dedication":
                continue

            value = block.get("value", {})
            photo = value.get("photo")

            if isinstance(photo, dict):
                # Extract image ID from old ImageBlock format
                image_id = photo.get("image")
                old_alt = photo.get("alt_text", "")

                # Set photo to just the image ID
                value["photo"] = image_id
                changed = True

                # If block-level alt_text is empty, copy from old ImageBlock
                if not value.get("alt_text") and old_alt:
                    value["alt_text"] = old_alt

        if changed:
            page.body = json.dumps(body_data)
            page.save(update_fields=["body"])


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
