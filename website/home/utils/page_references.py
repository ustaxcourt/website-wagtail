"""
Repoint every reference to one page at another page.

Wagtail stores internal links by page ID (rich text `<a linktype="page" id="..">`,
PageChooserBlock values, ForeignKeys), so deleting a page breaks them even if a
replacement page reuses its slug. Call repoint_page_references() before deleting
the old page.

Sources are found with Wagtail's ReferenceIndex (the same data behind the admin's
"Usage" tab), so the index must be current - run `rebuild_references_index` first
if in doubt.
"""

import logging

from django.contrib.contenttypes.models import ContentType
from django.db import models
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, ReferenceIndex, RevisionMixin
from wagtail.rich_text.rewriters import FIND_A_TAG, extract_attrs

logger = logging.getLogger(__name__)


def repoint_page_references(old_page: Page, new_page: Page) -> list[str]:
    """Point every indexed reference to old_page at new_page. Returns a log line per source object."""
    page_ct = ReferenceIndex._get_base_content_type(Page)
    sources = (
        ReferenceIndex.get_references_to(old_page)
        .values_list("content_type", "object_id")
        .distinct()
    )

    log = []
    for content_type_id, object_id in sources:
        model = ContentType.objects.get_for_id(content_type_id).model_class()
        source = model.objects.get(pk=object_id)
        if isinstance(source, Page) and source.pk == old_page.pk:
            continue  # links to itself go away with it

        # Live row (plus any child objects such as SideCards).
        dirty_fields, dirty_children = _repoint_object(
            source, page_ct.id, old_page.pk, new_page.pk
        )
        for child in dirty_children:
            child.save()
        if dirty_fields:
            if isinstance(source, Page):
                source.save(clean=False, update_fields=dirty_fields)
            else:
                source.save(update_fields=dirty_fields)

        # The editor loads the latest revision, not the live row, so patch that
        # too or the next save in the admin brings the old ID back.
        if isinstance(source, RevisionMixin) and source.latest_revision:
            revision = source.latest_revision
            revision_object = revision.as_object()
            if any(
                _repoint_object(revision_object, page_ct.id, old_page.pk, new_page.pk)
            ):
                revision.content = revision_object.serializable_data()
                revision.save(update_fields=["content"])

        log.append(f"{model.__name__} {object_id} ({source})")
        logger.info(f"Repointed references in {log[-1]}")

    return log


def _repoint_object(obj, page_ct_id, old_id, new_id):
    """Rewrite in memory; returns (dirty field names, dirty child objects)."""
    paths = {
        content_path
        for ct_id, object_id, _, content_path in ReferenceIndex._extract_references_from_object(
            obj
        )
        if ct_id == page_ct_id and object_id == str(old_id)
    }
    dirty_fields, dirty_children = set(), []
    for content_path in paths:
        target, field_name = _repoint_path(
            obj, [p for p in content_path.split(".") if p], old_id, new_id
        )
        if target is obj:
            dirty_fields.add(field_name)
        elif target not in dirty_children:
            dirty_children.append(target)
    return sorted(dirty_fields), dirty_children


def _repoint_path(obj, path, old_id, new_id):
    """Follow a ReferenceIndex content_path on obj and swap the ID at the end of it."""
    name, *rest = path
    field = _concrete_field(obj, name)

    if field is None:
        # Child relation: "<relation>.<child pk>.<rest of path>"
        child_pk, *rest = rest
        child = next(c for c in getattr(obj, name).all() if str(c.pk) == child_pk)
        target, _ = _repoint_path(child, rest, old_id, new_id)
        return target, None

    if isinstance(field, models.ForeignKey):
        setattr(obj, field.attname, new_id)
    elif isinstance(field, RichTextField):
        setattr(obj, name, _repoint_rich_text(getattr(obj, name), old_id, new_id))
    elif isinstance(field, StreamField):
        raw = field.stream_block.get_prep_value(getattr(obj, name))
        setattr(obj, name, _repoint_raw_block(raw, rest, old_id, new_id))
    else:
        raise ValueError(f"Don't know how to repoint {type(field).__name__} '{name}'")
    return obj, name


def _repoint_raw_block(node, path, old_id, new_id):
    """Walk raw StreamField JSON: lists are stream/list children keyed by block id, dicts are structs."""
    if not path:
        if isinstance(node, int) and node == old_id:  # PageChooserBlock
            return new_id
        if isinstance(node, str):  # RichTextBlock
            return _repoint_rich_text(node, old_id, new_id)
        raise ValueError(f"Unexpected value at end of content path: {node!r}")

    key, *rest = path
    if isinstance(node, list):
        item = next(item for item in node if item.get("id") == key)
        item["value"] = _repoint_raw_block(item["value"], rest, old_id, new_id)
    else:
        node[key] = _repoint_raw_block(node[key], rest, old_id, new_id)
    return node


def _repoint_rich_text(html, old_id, new_id):
    def replace(match):
        attrs = extract_attrs(match.group(1))
        if attrs.get("linktype") != "page" or attrs.get("id") != str(old_id):
            return match.group(0)
        return match.group(0).replace(f'id="{old_id}"', f'id="{new_id}"')

    return FIND_A_TAG.sub(replace, html)


def _concrete_field(obj, name):
    try:
        field = obj._meta.get_field(name)
    except Exception:
        return None
    return field if field.concrete else None
