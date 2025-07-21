from django.db import migrations, transaction
from wagtail.fields import StreamField

# --- Configuration ---
# This dictionary maps the OLD document title to the NEW document title.
# The migration will find the corresponding document objects based on these titles.
DOC_REPLACEMENTS = {
    "Rule-27.pdf": "Rule-27_Amended_03202023.pdf",
    "Rule-121.pdf": "Rule-121_Amended_03202023.pdf",
}

# --- Helper Functions ---


def get_document_id_map(apps):
    """
    Builds a mapping from old document IDs to new document IDs based on titles.
    """
    Document = apps.get_model("wagtaildocs", "Document")
    doc_id_map = {}
    for old_title, new_title in DOC_REPLACEMENTS.items():
        try:
            old_doc = Document.objects.get(title=old_title)
            new_doc = Document.objects.get(title=new_title)
            doc_id_map[old_doc.id] = new_doc.id
            print(
                f"  - Mapping doc '{old_title}' (ID: {old_doc.id}) to '{new_title}' (ID: {new_doc.id})"
            )
        except Document.DoesNotExist:
            print(
                f"WARNING: Could not find document '{old_title}' or '{new_title}'. Skipping this replacement."
            )
            continue
    return doc_id_map


def process_html_content(html, doc_id_map):
    """
    Processes a string of HTML, replacing document links.
    Returns the modified HTML and a list of replacements made.
    """
    replacements = []
    for old_id, new_id in doc_id_map.items():
        old_link_pattern = f'<a linktype="document" id="{old_id}"'
        if old_link_pattern in html:
            new_link_pattern = f'<a linktype="document" id="{new_id}"'
            html = html.replace(old_link_pattern, new_link_pattern)
            replacements.append((old_id, new_id))
    return html, replacements


def process_streamfield(stream_value, doc_id_map):
    """
    Recursively processes a StreamField's raw data to replace document links.
    Handles nested StreamFields and StructBlocks.
    """
    body_data = stream_value.raw_data
    replacements_made = []

    for block_data in body_data:
        # Process StructBlocks (like 'questionanswers')
        if isinstance(block_data.get("value"), dict):
            for key, value in block_data["value"].items():
                if isinstance(value, str) and '<a linktype="document"' in value:
                    new_value, replacements = process_html_content(value, doc_id_map)
                    if replacements:
                        block_data["value"][key] = new_value
                        replacements_made.extend(replacements)
        # Process lists of StructBlocks (like the items in 'questionanswers')
        elif isinstance(block_data.get("value"), list):
            for item in block_data.get("value", []):
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, str) and '<a linktype="document"' in value:
                            new_value, replacements = process_html_content(
                                value, doc_id_map
                            )
                            if replacements:
                                item[key] = new_value
                                replacements_made.extend(replacements)

    return body_data, replacements_made


# --- Main Migration Logic ---


def update_document_references(apps, schema_editor):
    """
    Finds the "Guidance for Petitioners: Starting A Case" page and updates
    its content to replace links to old documents with new ones.
    """
    EnhancedStandardPage = apps.get_model("home", "EnhancedStandardPage")
    PAGE_SLUG = "petitioners-start"

    print("\nStarting document reference migration...")
    doc_id_map = get_document_id_map(apps)

    if not doc_id_map:
        print("SKIPPING: No valid document mappings found. Ensure documents exist.")
        return

    try:
        page = EnhancedStandardPage.objects.get(slug=PAGE_SLUG)
        print(f"\nProcessing page: {page.title} (ID: {page.id})")
    except EnhancedStandardPage.DoesNotExist:
        print(f"SKIPPING: Page with slug '{PAGE_SLUG}' not found.")
        return

    page_changed = False
    total_replacements = 0

    # Iterate over all fields of the page model
    for field in page._meta.get_fields():
        # Check if the field is a StreamField
        if isinstance(field, StreamField):
            field_name = field.name
            stream_value = getattr(page, field_name)
            if stream_value and stream_value.raw_data:
                new_body, replacements = process_streamfield(stream_value, doc_id_map)
                if replacements:
                    setattr(page, field_name, new_body)
                    page_changed = True
                    total_replacements += len(replacements)
                    print(
                        f"  - Found {len(replacements)} replacements in StreamField '{field_name}'"
                    )

    if page_changed:
        with transaction.atomic():
            page.save()
        print(f"  → {total_replacements} total replacements made.")
        print(f"  → Page '{page.title}' has been updated and published.")
    else:
        print("  → No document references needed updating on this page.")

    print("\nMigration complete.")


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0058_fix_inline_pdf_links"),
        ("wagtaildocs", "0012_uploadeddocument"),
    ]

    operations = [
        migrations.RunPython(update_document_references, migrations.RunPython.noop),
    ]
