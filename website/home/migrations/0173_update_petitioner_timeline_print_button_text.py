import copy
import json
import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def _set_print_button_text(node):
    changed = False
    if isinstance(node, list):
        for item in node:
            changed |= _set_print_button_text(item)
    elif isinstance(node, dict):
        if node.get("type") == "detailed_timeline" and isinstance(
            node.get("value"), dict
        ):
            if (
                "print_button_text" not in node["value"]
                or node["value"]["print_button_text"] != "Print Detailed Timeline"
            ):
                node["value"]["print_button_text"] = "Print Detailed Timeline"
                changed = True
        for child in node.values():
            changed |= _set_print_button_text(child)
    return changed


def _convert_stream_json(raw):
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(data, list):
        return None
    return data if _set_print_button_text(data) else None


def migrate_print_button_text_for_petitioners_timeline_page(apps, schema_editor):
    EnhancedStandardPage = apps.get_model("home", "EnhancedStandardPage")
    Revision = apps.get_model("wagtailcore", "Revision")

    pages = 0
    revisions = 0
    for page in EnhancedStandardPage.objects.filter(
        slug="petitioners-timeline"
    ).iterator():
        data = _convert_stream_json(copy.deepcopy(list(page.body.raw_data)))
        if data is not None:
            page.body = json.dumps(data)
            page.save(update_fields=["body"])
            pages += 1

            for revision in Revision.objects.filter(
                object_id=page.page_ptr_id
            ).iterator():
                content = revision.content
                if not isinstance(content, dict) or "detailed_timeline" not in str(
                    content.get("body", "")
                ):
                    continue
                data = _convert_stream_json(content["body"])
                if data is not None:
                    content["body"] = json.dumps(data)
                    revision.content = content
                    revision.save(update_fields=["content"])
                    revisions += 1

    logger.info(
        "0173: modified %s page(s) and %s revision(s) to update detailed timeline's print button text.",
        pages,
        revisions,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0172_alter_enhancedstandardpage_body"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [
        migrations.RunPython(
            migrate_print_button_text_for_petitioners_timeline_page,
            migrations.RunPython.noop,
        ),
    ]
