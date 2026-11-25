import copy
import json
import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def _convert_phases(node):
    """Recursively convert every detailed_timeline phase in a StreamField JSON
    structure from show_info_icon to bubble_content. Returns True if changed."""
    changed = False
    if isinstance(node, list):
        for item in node:
            changed |= _convert_phases(item)
    elif isinstance(node, dict):
        if node.get("type") == "detailed_timeline" and isinstance(
            node.get("value"), dict
        ):
            for phase in node["value"].get("phases") or []:
                value = phase.get("value")
                if not isinstance(value, dict):
                    continue
                if "bubble_content" not in value:
                    value["bubble_content"] = (
                        "info" if value.get("show_info_icon") else "number"
                    )
                    changed = True
                if "show_info_icon" in value:
                    del value["show_info_icon"]
                    changed = True
        for child in node.values():
            changed |= _convert_phases(child)
    return changed


def _convert_stream_json(raw):
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(data, list):
        return None
    return data if _convert_phases(data) else None


def migrate_show_info_icon_to_bubble_content(apps, schema_editor):
    EnhancedStandardPage = apps.get_model("home", "EnhancedStandardPage")
    Revision = apps.get_model("wagtailcore", "Revision")

    pages = 0
    for page in EnhancedStandardPage.objects.all().iterator():
        data = _convert_stream_json(copy.deepcopy(list(page.body.raw_data)))
        if data is not None:
            page.body = json.dumps(data)
            page.save(update_fields=["body"])
            pages += 1

    revisions = 0
    for revision in Revision.objects.all().iterator():
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
        "0171: converted %s page(s) and %s revision(s) to bubble_content.",
        pages,
        revisions,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0170_alter_enhancedstandardpage_body"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [
        migrations.RunPython(
            migrate_show_info_icon_to_bubble_content,
            migrations.RunPython.noop,
        ),
    ]
