"""Data migration: convert image blocks from bare int format to
ImageWithLinkBlock StructBlock format.

Existing pages store image blocks as:
    {"type": "image", "value": 42}

The new ImageWithLinkBlock expects:
    {"type": "image", "value": {"image": 42, "link": []}}

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
                block["value"] = value["image"]
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
