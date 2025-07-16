from django.db import migrations

from home.data.document_tags_map import DOCUMENT_TAGS_MAP
from home.data.role_tag_tags_map import ROLE_TAGS_TAG_MAP


def assign_documents_role_tags(apps, schema_editor):
    Document = apps.get_model("wagtaildocs", "Document")
    Tag = apps.get_model("taggit", "Tag")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    ContentType = apps.get_model("contenttypes", "ContentType")
    doc_content_type = ContentType.objects.get(
        app_label="wagtaildocs", model="document"
    )

    for doc_name, data in DOCUMENT_TAGS_MAP.items():
        try:
            doc = Document.objects.get(file=f"documents/{doc_name}")
        except Document.DoesNotExist:
            print(f"Document with title '{doc_name}' does not exist.")
            continue
        doc_tags = data.get("tags", [])
        for role_tag, associated_tags in ROLE_TAGS_TAG_MAP.items():
            if set(associated_tags) & set(doc_tags):
                try:
                    tag = Tag.objects.get(name=role_tag)
                except Tag.DoesNotExist:
                    print(f"Tag with name '{role_tag}' does not exist.")
                    continue
                if not TaggedItem.objects.filter(
                    tag_id=tag.pk, object_id=doc.pk, content_type_id=doc_content_type.pk
                ).exists():
                    TaggedItem.objects.create(
                        tag_id=tag.pk,
                        object_id=doc.pk,
                        content_type_id=doc_content_type.pk,
                    )


def remove_documents_role_tags(apps, schema_editor):
    Document = apps.get_model("wagtaildocs", "Document")
    Tag = apps.get_model("taggit", "Tag")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    ContentType = apps.get_model("contenttypes", "ContentType")
    doc_content_type = ContentType.objects.get(
        app_label="wagtaildocs", model="document"
    )

    for doc_name, data in DOCUMENT_TAGS_MAP.items():
        try:
            doc = Document.objects.get(title=doc_name)
        except Document.DoesNotExist:
            print(f"Document with title '{doc_name}' does not exist.")
            continue
        doc_tags = data.get("tags", [])
        for role_tag, associated_tags in ROLE_TAGS_TAG_MAP.items():
            if set(associated_tags) & set(doc_tags):
                try:
                    tag = Tag.objects.get(name=role_tag)
                except Tag.DoesNotExist:
                    print(f"Tag with name '{role_tag}' does not exist.")
                    continue
                TaggedItem.objects.filter(
                    tag_id=tag.pk, object_id=doc.pk, content_type_id=doc_content_type.pk
                ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0061_add_role_tags"),
        ("wagtaildocs", "0001_initial"),
        ("taggit", "__latest__"),
    ]
    operations = [
        migrations.RunPython(assign_documents_role_tags, remove_documents_role_tags),
    ]
