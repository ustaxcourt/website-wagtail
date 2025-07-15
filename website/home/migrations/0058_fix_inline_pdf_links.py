# Generated manually

import re
import logging
from django.db import migrations, transaction
from wagtail.models import Page
from wagtail.documents import get_document_model
from wagtail.rich_text import RichText

logger = logging.getLogger(__name__)


def fix_inline_pdf_links(apps, schema_editor):
    """
    Convert inline PDF links from <a href="/media/documents/file.pdf"> format
    to proper Wagtail document references <a linktype="document" id="document.id">
    """
    Document = get_document_model()
    processed_pages = 0
    total_replacements = 0

    print("Starting PDF link conversion migration...")

    def find_document_by_filename(filename):
        """Find Wagtail document by filename"""
        try:
            # Try exact filename match first
            document = Document.objects.filter(file__icontains=filename).first()

            if not document:
                # Try without extension
                base_filename = filename.rsplit(".", 1)[0]
                document = Document.objects.filter(
                    file__icontains=base_filename
                ).first()

            return document
        except Exception as e:
            logger.warning(f"Error finding document {filename}: {e}")
            return None

    def process_html_content(html_content):
        """Process HTML content and replace PDF links"""
        if not html_content or "<a href=" not in html_content:
            return html_content, []

        # Pattern to match PDF links: <a href="path/to/file.pdf" ...>text</a>
        pdf_link_pattern = r'<a\s+href="([^"]*\.pdf)"([^>]*)>(.*?)</a>'

        replacements = []

        def replace_link(match):
            nonlocal replacements

            pdf_url = match.group(1)
            other_attrs = match.group(2)
            link_text = match.group(3)

            # Extract filename from URL
            filename = pdf_url.split("/")[-1]

            # Find document by filename
            document = find_document_by_filename(filename)

            if document:
                # Track the replacement
                replacements.append((filename, document.title, document.id))

                # Create new link with document reference
                new_link = f'<a linktype="document" id="{document.id}" {other_attrs}>{link_text}</a>'
                return new_link
            else:
                print(f"    Document not found for: {filename}")
                return match.group(0)  # Return original if document not found

        new_content = re.sub(
            pdf_link_pattern,
            replace_link,
            html_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        return new_content, replacements

    def process_struct_block(struct_value):
        """Process StructBlock content"""
        page_replacements = []

        for key, value in struct_value.items():
            if hasattr(value, "source"):  # RichTextBlock content
                new_content, block_replacements = process_html_content(value.source)
                if block_replacements:
                    struct_value[key] = value.__class__(new_content)
                    page_replacements.extend(block_replacements)
            elif isinstance(value, RichText):  # RichText content
                new_content, block_replacements = process_html_content(str(value))
                if block_replacements:
                    struct_value[key] = RichText(new_content)
                    page_replacements.extend(block_replacements)
            elif isinstance(value, str):  # String content
                new_content, block_replacements = process_html_content(value)
                if block_replacements:
                    struct_value[key] = new_content
                    page_replacements.extend(block_replacements)
            elif isinstance(value, dict):
                block_replacements = process_struct_block(value)
                page_replacements.extend(block_replacements)
            elif isinstance(value, list):
                block_replacements = process_list_block(value)
                page_replacements.extend(block_replacements)

        return page_replacements

    def process_list_block(list_value):
        """Process ListBlock content"""
        page_replacements = []

        for i, item in enumerate(list_value):
            if hasattr(item, "source"):  # RichTextBlock in list
                new_content, block_replacements = process_html_content(item.source)
                if block_replacements:
                    list_value[i] = item.__class__(new_content)
                    page_replacements.extend(block_replacements)
            elif hasattr(item, "items"):  # StructValue in list
                block_replacements = process_struct_block(item)
                page_replacements.extend(block_replacements)
            elif isinstance(item, dict):
                block_replacements = process_struct_block(item)
                page_replacements.extend(block_replacements)
            elif isinstance(item, list):
                block_replacements = process_list_block(item)
                page_replacements.extend(block_replacements)
            elif isinstance(item, str):
                new_content, block_replacements = process_html_content(item)
                if block_replacements:
                    list_value[i] = new_content
                    page_replacements.extend(block_replacements)

        return page_replacements

    def process_streamfield(streamfield):
        """Process StreamField content recursively"""
        page_replacements = []

        for block in streamfield:
            if hasattr(block, "value"):
                if hasattr(block.value, "source"):  # RichTextBlock
                    new_content, block_replacements = process_html_content(
                        block.value.source
                    )
                    if block_replacements:
                        block.value = block.value.__class__(new_content)
                        page_replacements.extend(block_replacements)
                elif hasattr(block.value, "items"):  # StructBlock or StructValue
                    block_replacements = process_struct_block(block.value)
                    page_replacements.extend(block_replacements)
                elif isinstance(block.value, dict):  # Dict-like StructBlock
                    block_replacements = process_struct_block(block.value)
                    page_replacements.extend(block_replacements)
                elif hasattr(block.value, "__iter__") and not isinstance(
                    block.value, str
                ):  # ListBlock
                    block_replacements = process_list_block(block.value)
                    page_replacements.extend(block_replacements)
                elif isinstance(block.value, str):  # String content
                    new_content, block_replacements = process_html_content(block.value)
                    if block_replacements:
                        block.value = new_content
                        page_replacements.extend(block_replacements)

        return streamfield, page_replacements

    def process_single_page(page):
        """Process a single page and fix inline PDF links"""
        print(f"Processing page: {page.title} (ID: {page.id}, slug: {page.slug})")

        page_changed = False
        page_replacements = []

        # Process StreamField content (like 'body' field)
        if hasattr(page, "body") and page.body:
            new_body, body_replacements = process_streamfield(page.body)
            if body_replacements:
                page.body = new_body
                page_changed = True
                page_replacements.extend(body_replacements)

        # Process any other RichTextFields
        for field in page._meta.get_fields():
            if hasattr(field, "editable") and field.editable:
                field_name = field.name
                if field_name not in ["body", "id", "path", "depth", "num_child"]:
                    field_value = getattr(page, field_name, None)
                    if isinstance(field_value, str) and "<a href=" in field_value:
                        new_value, field_replacements = process_html_content(
                            field_value
                        )
                        if field_replacements:
                            setattr(page, field_name, new_value)
                            page_changed = True
                            page_replacements.extend(field_replacements)

        if page_changed:
            with transaction.atomic():
                page.save()

        if page_replacements:
            # Show detailed replacement info
            for filename, doc_title, doc_id in page_replacements:
                print(
                    f"    → Replaced: {filename} (Document: {doc_title}, ID: {doc_id})"
                )

            print(f"  → {len(page_replacements)} replacements made")
            return len(page_replacements)

        return 0

    # Process all live pages
    pages_with_content = Page.objects.live().specific()

    for page in pages_with_content:
        replacements = process_single_page(page)
        if replacements > 0:
            processed_pages += 1
            total_replacements += replacements

    print(
        f"Migration complete. Pages processed: {processed_pages}, Total replacements: {total_replacements}"
    )


def reverse_fix_inline_pdf_links(apps, schema_editor):
    """
    This migration is irreversible since we're converting from hardcoded URLs
    to document references. Reversing would require storing the original URLs
    which we don't do for simplicity.
    """
    print(
        "This migration cannot be reversed - PDF links have been converted to document references"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0057_fix_petitioner_about_page"),
    ]

    operations = [
        migrations.RunPython(
            fix_inline_pdf_links,
            reverse_fix_inline_pdf_links,
            atomic=False,  # We handle transactions manually for better control
        ),
    ]
