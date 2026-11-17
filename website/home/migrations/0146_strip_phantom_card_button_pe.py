import json

from django.db import migrations


def strip_phantom_card_button(apps, schema_editor):
    """
    Card's 'buttons' field is a ListBlock(ButtonBlock(), ...) with no explicit
    `default`. Wagtail's ListBlock.__init__ falls back to a list containing one
    default-valued child (`[self.child_block.get_default()]`) whenever
    `default` isn't passed - so any card whose raw data omitted the 'buttons'
    key entirely (every card defined before this field existed, e.g. in
    home/management/commands/pages/rules_and_guidance/case_procedure_page.py)
    was silently given one Button with a required-but-blank 'text' and an
    empty required 'url', instead of an empty buttons list. That phantom
    button renders as nothing on the public site (the template loops over
    button.url, which has zero items), but fails full_clean() the moment an
    editor opens the page, since 'text' and 'url' are both required.

    home/models/pages/enhanced_standard.py now passes `default=[]` so this
    can't happen to newly-created cards, but any card that was already
    constructed (or re-saved) under the old default needs its stored JSON
    repaired directly. This targets any 'card' block, at any nesting depth,
    whose 'buttons' list contains an entry with a blank 'text' or an empty
    'url' - the two required fields a real button could never have been
    published with - since such an entry can only be this phantom default,
    never legitimate authored content.

    Follows the same approach as 0141_migrate_card_block_icon_field_pe:
    intercepting the raw StreamField JSON directly via SQL (rather than
    `page.body` through the historical model) and reconciling
    wagtailcore_revision snapshots too, so previewing or reverting to an old
    revision doesn't resurrect the phantom button.
    """
    connection = schema_editor.connection
    is_postgres = connection.vendor == "postgresql"

    def is_phantom_button(button_item):
        # Each ListBlock entry is stored as {"type": "item", "value": {...}, "id": ...},
        # not the button's fields directly.
        button = button_item.get("value") if isinstance(button_item, dict) else None
        return (
            not isinstance(button, dict)
            or not button.get("text")
            or not button.get("url")
        )

    def strip_card_item(card_item):
        card = card_item.get("value") if isinstance(card_item, dict) else None
        if not isinstance(card, dict):
            return card_item
        buttons = card.get("buttons")
        if isinstance(buttons, list) and any(is_phantom_button(b) for b in buttons):
            card_item = dict(card_item)
            card = dict(card)
            card["buttons"] = [b for b in buttons if not is_phantom_button(b)]
            card_item["value"] = card
        return card_item

    def walk(value):
        if isinstance(value, list):
            return [walk(item) for item in value]
        if isinstance(value, dict):
            if value.get("type") == "card" and isinstance(value.get("value"), list):
                value = dict(value)
                value["value"] = [
                    strip_card_item(card_item) for card_item in value["value"]
                ]
                return value
            return {key: walk(item) for key, item in value.items()}
        return value

    body_column = "body::text" if is_postgres else "body"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT page_ptr_id, {body_column} FROM home_enhancedstandardpage "  # noqa: S608
            f"WHERE {body_column} LIKE %s",
            ['%"buttons"%'],
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
        # Same bare-substring-match rationale as 0141: revision.content
        # double-encodes 'body' as a JSON string, so an escaped-quote LIKE
        # pattern would be Postgres-backslash-fragile. False positives are
        # harmless since the JSON walk() above decides what actually changes.
        cursor.execute(
            f"SELECT id, {content_column} FROM wagtailcore_revision "  # noqa: S608
            f"WHERE {content_column} LIKE %s",
            ["%buttons%"],
        )
        revision_rows = cursor.fetchall()

    for revision_id, raw_content in revision_rows:
        content = (
            json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        )
        raw_body = content.get("body")
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
        ("home", "0145_split_oversized_card_sets_pe"),
    ]

    operations = [
        migrations.RunPython(strip_phantom_card_button, migrations.RunPython.noop),
    ]
