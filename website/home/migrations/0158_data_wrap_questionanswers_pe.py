"""
Data migration: wrap existing ``questionanswers`` blocks in the new struct shape.

0157 changed the EnhancedStandardPage ``questionanswers`` block from a bare list of
Q&As to a struct of ``{"display_filter_section": bool, "questions": [...]}``. This
rewrites saved content to match, with ``display_filter_section`` off so existing
pages render as before.

Only the ``body`` field is touched - EnhancedRawHTMLPage's ``raw_html_body`` has its
own ``questionanswers`` block that keeps the list shape. The walk is recursive so
Q&As nested inside other blocks (anchor pages, card tile default content) are
covered, and it is idempotent so re-running it changes nothing.

Wagtail's MigrateStreamData isn't used because it only migrates revisions whose
content type is exactly EnhancedStandardPage, missing every subclass page
(PetitionerExperiencePage, PressReleasePage, etc.).
"""

import json

from django.db import migrations
from django.db.models import F, JSONField
from django.db.models.functions import Cast
from wagtail.blocks import StreamValue

QA_BLOCK_TYPE = "questionanswers"
CHUNK_SIZE = 500


def wrap_qa_blocks(node):
    """Return ``(node, changed)`` with every list-shaped Q&A block wrapped."""
    changed = False
    if isinstance(node, dict):
        if node.get("type") == QA_BLOCK_TYPE and isinstance(node.get("value"), list):
            node["value"] = {
                "display_filter_section": False,
                "questions": node["value"],
            }
            changed = True
        for value in node.values():
            changed = wrap_qa_blocks(value)[1] or changed
    elif isinstance(node, list):
        for value in node:
            changed = wrap_qa_blocks(value)[1] or changed
    return node, changed


def unwrap_qa_blocks(node):
    """Inverse of ``wrap_qa_blocks``; drops ``display_filter_section``."""
    changed = False
    if isinstance(node, dict):
        value = node.get("value")
        if node.get("type") == QA_BLOCK_TYPE and isinstance(value, dict):
            node["value"] = value.get("questions") or []
            changed = True
        for value in node.values():
            changed = unwrap_qa_blocks(value)[1] or changed
    elif isinstance(node, list):
        for value in node:
            changed = unwrap_qa_blocks(value)[1] or changed
    return node, changed


def _transform_pages(apps, transform):
    EnhancedStandardPage = apps.get_model("home", "EnhancedStandardPage")
    stream_block = EnhancedStandardPage._meta.get_field("body").stream_block
    pages = EnhancedStandardPage.objects.annotate(
        raw_body=Cast(F("body"), JSONField())
    ).values_list("pk", "raw_body")
    for pk, raw_body in pages.iterator(chunk_size=CHUNK_SIZE):
        raw_body, changed = transform(raw_body)
        if changed:
            EnhancedStandardPage.objects.filter(pk=pk).update(
                body=StreamValue(stream_block, raw_body, is_lazy=True)
            )


def _transform_revisions(apps, transform):
    EnhancedStandardPage = apps.get_model("home", "EnhancedStandardPage")
    Revision = apps.get_model("wagtailcore", "Revision")
    page_ids = [
        str(pk) for pk in EnhancedStandardPage.objects.values_list("pk", flat=True)
    ]
    revisions = Revision.objects.filter(
        base_content_type__app_label="wagtailcore",
        base_content_type__model="page",
        object_id__in=page_ids,
    )
    buffer = []
    for revision in revisions.iterator(chunk_size=CHUNK_SIZE):
        body = revision.content.get("body")
        if not isinstance(body, str) or QA_BLOCK_TYPE not in body:
            continue
        data, changed = transform(json.loads(body))
        if changed:
            revision.content["body"] = json.dumps(data)
            buffer.append(revision)
        if len(buffer) >= CHUNK_SIZE:
            Revision.objects.bulk_update(buffer, ["content"])
            buffer = []
    if buffer:
        Revision.objects.bulk_update(buffer, ["content"])


def forwards(apps, schema_editor):
    _transform_pages(apps, wrap_qa_blocks)
    _transform_revisions(apps, wrap_qa_blocks)


def backwards(apps, schema_editor):
    _transform_pages(apps, unwrap_qa_blocks)
    _transform_revisions(apps, unwrap_qa_blocks)


class Migration(migrations.Migration):
    dependencies = [("home", "0157_alter_enhancedstandardpage_body_pe")]

    operations = [migrations.RunPython(forwards, backwards)]
