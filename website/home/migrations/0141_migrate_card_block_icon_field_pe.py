import json

from django.db import migrations


def migrate_card_icon_field(apps, schema_editor):
    """
    The 'card' StreamField block used to have a single 'icon' field. It has been
    replaced by 'numbered_icon' (plus other new fields) as part of WAG-1338.
    Any already-published EnhancedStandardPage content using the old 'icon' key
    would otherwise silently lose its icon, since StructBlock ignores unknown
    keys.

    Note: unlike most StreamField data migrations in this codebase (e.g. 0132's
    back-button backfill), this can't use `apps.get_model(...)` + `page.body`
    the normal way. Since migration 0140 (which this depends on) already
    swapped in the *new* block definitions, reading `page.body` through the
    historical model would deserialize old cards using the new schema first -
    silently dropping the unrecognized 'icon' key via StructBlock.to_python()
    before this code ever saw it. So this instead reads/writes the raw
    StreamField JSON directly via SQL, intercepting the old 'icon' key before
    any block-schema-aware deserialization happens, and renames it to
    'numbered_icon' wherever a 'card' block is found, at any nesting depth
    (e.g. inside Card Tiles default content or Anchor Page body).
    """
    connection = schema_editor.connection
    # On Postgres, `body` is a jsonb column - LIKE has no jsonb operator, and an
    # uncast SELECT would hand back already-parsed Python objects instead of the
    # JSON string `json.loads` below expects. SQLite stores it as a plain TEXT
    # column, where `body` and `body::text` behave the same, so this only needs
    # a Postgres-specific cast rather than a per-backend branch.
    body_column = "body::text" if connection.vendor == "postgresql" else "body"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT page_ptr_id, {body_column} FROM home_enhancedstandardpage "  # noqa: S608
            f"WHERE {body_column} LIKE %s",
            ['%"card"%'],
        )
        rows = cursor.fetchall()

    def migrate_card_value(card):
        if "icon" in card and "numbered_icon" not in card:
            card = dict(card)
            card["numbered_icon"] = card.pop("icon")
            card.setdefault("numbered_icon_alignment", "center")
        return card

    def walk(value):
        if isinstance(value, list):
            return [walk(item) for item in value]
        if isinstance(value, dict):
            if value.get("type") == "card" and isinstance(value.get("value"), list):
                value = dict(value)
                value["value"] = [migrate_card_value(card) for card in value["value"]]
                return value
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
        ("home", "0140_alter_enhancedstandardpage_body_pe"),
    ]

    operations = [
        migrations.RunPython(migrate_card_icon_field, migrations.RunPython.noop),
    ]
