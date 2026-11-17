import json
import uuid

from django.db import migrations


def split_oversized_card_sets(apps, schema_editor):
    """
    The 'card' StreamField block (ListBlock) had no maximum until WAG-1338
    capped it at 3, to match the Petitioner Experience card designs. Any
    already-published EnhancedStandardPage content with more than 3 cards in
    a single block (e.g. the "Case Procedure Information" page, seeded years
    before this cap existed) would keep rendering fine - Wagtail only
    enforces `max_num` on save, not on read - but would fail validation the
    next time an editor opened and saved that page, until they manually split
    the cards themselves.

    This splits any such oversized 'card' block into consecutive 3-card (or
    fewer) blocks in its place, same as the updated seed data now does for
    fresh installs. Runs after 0141 (icon field rename) so every card here
    already matches the current schema. Uses the same raw-JSON approach as
    0141, at any nesting depth, for the same reason: reading through the
    model would already be safe here (no field is being dropped), but raw SQL
    keeps this consistent with 0141 and avoids a StreamField round-trip.
    """
    connection = schema_editor.connection
    body_column = "body::text" if connection.vendor == "postgresql" else "body"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT page_ptr_id, {body_column} FROM home_enhancedstandardpage "  # noqa: S608
            f"WHERE {body_column} LIKE %s",
            ['%"card"%'],
        )
        rows = cursor.fetchall()

    def split_card_block(block):
        cards = block["value"]
        chunks = [cards[i : i + 3] for i in range(0, len(cards), 3)]
        return [
            {**block, "value": chunk}
            if i == 0
            else {**block, "value": chunk, "id": str(uuid.uuid4())}
            for i, chunk in enumerate(chunks)
        ]

    def walk(value):
        if isinstance(value, list):
            new_list = []
            for item in value:
                if (
                    isinstance(item, dict)
                    and item.get("type") == "card"
                    and isinstance(item.get("value"), list)
                    and len(item["value"]) > 3
                ):
                    new_list.extend(split_card_block(item))
                else:
                    new_list.append(walk(item))
            return new_list
        if isinstance(value, dict):
            return {key: walk(item) for key, item in value.items()}
        return value

    for page_id, raw_body in rows:
        data = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        migrated = walk(data)
        if migrated != data:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                    [json.dumps(migrated), page_id],
                )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0144_migrate_card_block_icon_field_pe"),
    ]

    operations = [
        migrations.RunPython(split_oversized_card_sets, migrations.RunPython.noop),
    ]
