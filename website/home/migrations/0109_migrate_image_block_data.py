"""Data migration: convert image blocks to ImageWithLinkBlock StructBlock format.

Existing pages may store image blocks in one of two legacy formats:

  1. Bare integer (old ImageChooserBlock format):
         {"type": "image", "value": 42}

  2. ImageBlock dict (old ImageBlock format):
         {"type": "image", "value": {"image": 42, "alt_text": "...", "decorative": false}}

The new ImageWithLinkBlock expects the image to be nested under an ``image`` key
and a ``link`` StreamBlock list alongside it:

    {"type": "image", "value": {"image": {"image": 42, ...}, "link": []}}

This must run before update_index or any StreamField deserialization
of pages containing old-format image blocks.
"""

import json

from django.db import migrations


def convert_image_block_data(apps, schema_editor):
    """Use raw SQL to avoid StreamField deserialization issues in migrations."""
    connection = schema_editor.connection
    cursor = connection.cursor()

    cursor.execute("SELECT page_ptr_id, body FROM home_enhancedstandardpage")
    rows = cursor.fetchall()

    for page_id, body_raw in rows:
        if not body_raw:
            continue

        body_data = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

        if not isinstance(body_data, list):
            continue

        changed = False
        for block in body_data:
            if block.get("type") != "image":
                continue

            value = block.get("value")

            if isinstance(value, int):
                # Old bare-int format → wrap into nested ImageBlock dict then ImageWithLinkBlock
                block["value"] = {"image": {"image": value}, "link": []}
                changed = True
            elif isinstance(value, dict) and "link" not in value:
                # Old ImageBlock dict format (e.g. {"image": <id>, "alt_text": ..., "decorative": ...})
                # → wrap into ImageWithLinkBlock, preserving the existing ImageBlock data
                block["value"] = {"image": value, "link": []}
                changed = True

        if changed:
            cursor.execute(
                "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                [json.dumps(body_data), page_id],
            )


def reverse_migration(apps, schema_editor):
    """Reverse: convert back to bare int format."""
    connection = schema_editor.connection
    cursor = connection.cursor()

    cursor.execute("SELECT page_ptr_id, body FROM home_enhancedstandardpage")
    rows = cursor.fetchall()

    for page_id, body_raw in rows:
        if not body_raw:
            continue

        body_data = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

        if not isinstance(body_data, list):
            continue

        changed = False
        for block in body_data:
            if block.get("type") != "image":
                continue

            value = block.get("value")
            if isinstance(value, dict) and "image" in value:
                image_block_val = value["image"]
                image_id = None
                if isinstance(image_block_val, dict):
                    # image_block_val is an ImageBlock dict: {"image": <int_id>, ...}
                    inner = image_block_val.get("image")
                    if isinstance(inner, int):
                        image_id = inner
                elif isinstance(image_block_val, int):
                    image_id = image_block_val
                if image_id is not None:
                    block["value"] = image_id
                    changed = True

        if changed:
            cursor.execute(
                "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                [json.dumps(body_data), page_id],
            )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0108_alter_enhancedstandardpage_body"),
    ]

    operations = [
        migrations.RunPython(convert_image_block_data, reverse_migration),
    ]
