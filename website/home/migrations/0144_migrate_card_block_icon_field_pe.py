import json

from django.db import migrations

# The old 'icon' field accepted the full IconCategories set (book, file, PDF,
# user, etc.), but the new 'numbered_icon' field only accepts a status/step
# indicator: None, One, Two, Three, Check, or Exclamation. Only values with a
# direct equivalent are carried over below; anything else (e.g. a decorative
# icon like "book" or "file-pdf") has no numbered_icon counterpart and is
# dropped rather than written into the narrowed choice field as an invalid
# value - the alternative Copilot flagged as unsafe on this migration.
LEGACY_ICON_TO_NUMBERED_ICON = {
    "": "",
    "fa-solid fa-check": "fa-solid fa-check",
    "fa-solid fa-exclamation": "fa-solid fa-exclamation",
}


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

    Also reconciles existing page revision snapshots (wagtailcore_revision),
    not just the live home_enhancedstandardpage row: Wagtail stores each
    revision's full serialized field set separately, so previewing, reverting
    to, or approving an old revision after this migration would otherwise
    restore a copy of 'body' with the pre-migration 'icon' key intact.
    """
    connection = schema_editor.connection
    # On Postgres, `body`/`content` are jsonb columns - LIKE has no jsonb
    # operator, and an uncast SELECT would hand back already-parsed Python
    # objects instead of the JSON string `json.loads` below expects. SQLite
    # stores them as plain TEXT columns, where the cast is a no-op, so this
    # only needs a Postgres-specific cast rather than a per-backend branch.
    is_postgres = connection.vendor == "postgresql"

    def migrate_card_value(card):
        if "icon" in card and "numbered_icon" not in card:
            card = dict(card)
            old_icon = card.pop("icon")
            if old_icon in LEGACY_ICON_TO_NUMBERED_ICON:
                card["numbered_icon"] = LEGACY_ICON_TO_NUMBERED_ICON[old_icon]
                card.setdefault("numbered_icon_alignment", "center")
            else:
                print(  # noqa: T201
                    f"0141_migrate_card_block_icon_field_pe: dropping legacy "
                    f"icon {old_icon!r} with no numbered_icon equivalent"
                )
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

    body_column = "body::text" if is_postgres else "body"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT page_ptr_id, {body_column} FROM home_enhancedstandardpage "  # noqa: S608
            f"WHERE {body_column} LIKE %s",
            ['%"card"%'],
        )
        rows = cursor.fetchall()

    for page_id, raw_body in rows:
        data = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        migrated = walk(data)
        if migrated != data:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE home_enhancedstandardpage SET body = %s WHERE page_ptr_id = %s",
                    [json.dumps(migrated), page_id],
                )

    content_column = "content::text" if is_postgres else "content"
    with connection.cursor() as cursor:
        # revision.content is a JSONField whose own 'body' value is itself a
        # JSON-encoded string (Wagtail double-encodes StreamField data in
        # revision snapshots), so any quotes inside it are backslash-escaped
        # in the outer column's raw text. A pattern like '%"card"%' would
        # need a literal backslash to match that escaped form, but Postgres'
        # LIKE treats backslash as its own escape character by default, so
        # matching on that would be backend-fragile. Searching for the bare
        # words instead sidesteps quoting entirely; any false-positive rows
        # are harmless since the JSON walk below is what actually decides
        # whether a row needs rewriting.
        cursor.execute(
            f"SELECT id, {content_column} FROM wagtailcore_revision "  # noqa: S608
            f"WHERE {content_column} LIKE %s AND {content_column} LIKE %s",
            ["%card%", "%icon%"],
        )
        revision_rows = cursor.fetchall()

    for revision_id, raw_content in revision_rows:
        content = (
            json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        )
        raw_body = content.get("body")
        # Skip revisions with no 'body' field (e.g. snippets, non-page
        # models) - only page revisions with a StreamField body are relevant.
        if not isinstance(raw_body, str):
            continue

        body_data = json.loads(raw_body)
        migrated_body = walk(body_data)
        if migrated_body != body_data:
            content["body"] = json.dumps(migrated_body)
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE wagtailcore_revision SET content = %s WHERE id = %s",
                    [json.dumps(content), revision_id],
                )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0143_alter_enhancedstandardpage_body_pe"),
    ]

    operations = [
        migrations.RunPython(migrate_card_icon_field, migrations.RunPython.noop),
    ]
