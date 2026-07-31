"""
Management command to check for dangling references in the Home page
and its children pages.
"""

import logging
from django.core.management.base import BaseCommand
from wagtail.models import Page
from wagtail_transfer.serializers import serializer_registry
import django

django.setup()

logger = logging.getLogger(__name__)


def find_dangling_refs(root_page_id):
    root_page = Page.objects.get(pk=root_page_id)
    pages = root_page.get_descendants(inclusive=True).specific()

    object_references = set()
    models_to_serialize = set(pages)
    serialized_models = set()
    serialize_errors = []

    while models_to_serialize:
        model = models_to_serialize.pop()
        serialized_models.add(model)
        try:
            serializer = serializer_registry.get_model_serializer(type(model))
            object_references.update(serializer.get_object_references(model))
            models_to_serialize.update(
                serializer.get_objects_to_serialize(model).difference(serialized_models)
            )
        except Exception as e:
            serialize_errors.append(
                (type(model).__name__, getattr(model, "pk", None), repr(e))
            )

    exists_cache = {}

    def exists(model, pk):
        key = (model, pk)
        if key not in exists_cache:
            exists_cache[key] = model.objects.filter(pk=pk).exists()
        return exists_cache[key]

    broken = sorted(
        (model._meta.label_lower, pk)
        for model, pk in object_references
        if not exists(model, pk)
    )

    return {
        "objects_walked": len(serialized_models),
        "references_checked": len(object_references),
        "broken_references": broken,
        "serialize_errors": serialize_errors,
    }


def find_pages_holding_reference(broken_model_label, broken_pk, root_page_id):
    """Given a broken (model_label, pk) from find_dangling_refs, find which
    specific page(s) hold that reference, by re-checking each page's own
    direct get_object_references() individually."""
    from django.apps import apps

    model = apps.get_model(*broken_model_label.split("."))
    root_page = Page.objects.get(pk=root_page_id)
    pages = root_page.get_descendants(inclusive=True).specific()

    holders = []
    for page in pages:
        try:
            serializer = serializer_registry.get_model_serializer(type(page))
            refs = serializer.get_object_references(page)
        except Exception:
            continue
        for m, pk in refs:
            if m is model and pk == broken_pk:
                holders.append((page.pk, page.title, type(page).__name__))
    return holders


class Command(BaseCommand):
    help = "Check for dangling references in the Home page and its children pages"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "--page-id",
            type=int,
            help="Specify the page ID to start search from",
        )

    def handle(self, *args, **options):
        # self.dry_run = options.get("dry_run", False)
        # self.verbose = options.get("verbose", False)

        # Page to start the traversal from.
        PAGE_ID_TO_TRAVERSE_FROM = options.get("page_id")
        if PAGE_ID_TO_TRAVERSE_FROM is None:
            rootPageFirstChild = Page.get_first_root_node().get_first_child()
            if rootPageFirstChild is not None:
                PAGE_ID_TO_TRAVERSE_FROM = rootPageFirstChild.id

        result = find_dangling_refs(PAGE_ID_TO_TRAVERSE_FROM)
        logger.info(f"Starting Page ID: {PAGE_ID_TO_TRAVERSE_FROM}")
        logger.info(f"Objects walked: {result['objects_walked']}")
        logger.info(f"References checked: {result['references_checked']}")
        logger.info(f"Broken references: {len(result['broken_references'])}")
        for label, pk in result["broken_references"]:
            holders = find_pages_holding_reference(label, pk, PAGE_ID_TO_TRAVERSE_FROM)
            logger.info(f"  {label} pk={pk} referenced by: {holders}")
        if result["serialize_errors"]:
            logger.info("Serialize errors (object couldn't even be walked):")
            for e in result["serialize_errors"]:
                logger.info(" ", e)
