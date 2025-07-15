"""
Management command to fix inline PDF links in Wagtail pages.

This script replaces hardcoded <a href="file.url"> links with proper Wagtail
document references using <a linktype="document" id="document.id"> format.
"""

import re
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page
from wagtail.documents import get_document_model
from wagtail.rich_text import RichText

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Replace inline PDF links with proper Wagtail document references"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Document = get_document_model()
        self.processed_pages = 0
        self.total_replacements = 0
        self.page_replacements = []  # Track replacements per page

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making actual changes",
        )
        parser.add_argument(
            "--page-id",
            type=int,
            help="Process only a specific page by ID",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed processing information",
        )

    def handle(self, *args, **options):
        self.dry_run = options.get("dry_run", False)
        self.verbose = options.get("verbose", False)
        page_id = options.get("page_id")

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        if page_id:
            try:
                page = Page.objects.get(id=page_id).specific
                self.process_single_page(page)
            except Page.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Page with ID {page_id} not found"))
                return
        else:
            self.process_all_pages()

        self.stdout.write(
            self.style.SUCCESS(
                f"Processing complete. Pages processed: {self.processed_pages}, "
                f"Total replacements: {self.total_replacements}"
            )
        )

        if self.total_replacements == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No PDF links found. If you expected to find links, "
                    "make sure pages have been initialized with 'make create_pages'"
                )
            )

    def process_all_pages(self):
        """Process all pages in the system"""
        # Get all page types that might contain StreamField or RichTextField content
        pages_with_content = Page.objects.live().specific()

        for page in pages_with_content:
            self.process_single_page(page)

    def process_single_page(self, page):
        """Process a single page and fix inline PDF links"""
        self.stdout.write(
            f"Processing page: {page.title} (ID: {page.id}, slug: {page.slug})"
        )

        page_changed = False
        self.page_replacements = []  # Reset for this page

        # Debug output for verbose mode
        if hasattr(self, "verbose") and self.verbose:
            self.stdout.write(f"  Page type: {type(page).__name__}")
            if hasattr(page, "body") and page.body:
                self.stdout.write(f"  Body length: {len(page.body)}")

        # Process StreamField content (like 'body' field)
        if hasattr(page, "body") and page.body:
            if hasattr(self, "verbose") and self.verbose:
                self.stdout.write(f"  Processing {len(page.body)} blocks in body field")
            new_body, body_replacements = self.process_streamfield(page.body)
            if body_replacements > 0:
                page.body = new_body
                page_changed = True

        # Process any other RichTextFields
        for field in page._meta.get_fields():
            if hasattr(field, "editable") and field.editable:
                field_name = field.name
                if field_name not in ["body", "id", "path", "depth", "num_child"]:
                    field_value = getattr(page, field_name, None)
                    if isinstance(field_value, str) and "<a href=" in field_value:
                        new_value, field_replacements = self.process_html_content(
                            field_value
                        )
                        if field_replacements > 0:
                            setattr(page, field_name, new_value)
                            page_changed = True

        if page_changed and not self.dry_run:
            with transaction.atomic():
                page.save()

        if self.page_replacements:
            self.processed_pages += 1
            self.total_replacements += len(self.page_replacements)

            # Show detailed replacement info
            for filename, doc_title, doc_id in self.page_replacements:
                self.stdout.write(
                    f"    → Replaced: {filename} (Document: {doc_title}, ID: {doc_id})"
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"  → {len(self.page_replacements)} replacements made"
                )
            )

    def process_streamfield(self, streamfield):
        """Process StreamField content recursively"""
        replacements = 0

        for i, block in enumerate(streamfield):
            if hasattr(self, "verbose") and self.verbose:
                self.stdout.write(
                    f"    Block {i}: {block.block_type}, value type: {type(block.value)}"
                )

            if hasattr(block, "value"):
                if hasattr(block.value, "source"):  # RichTextBlock
                    new_content, block_replacements = self.process_html_content(
                        block.value.source
                    )
                    if block_replacements > 0:
                        block.value = block.value.__class__(new_content)
                        replacements += block_replacements
                elif hasattr(block.value, "items"):  # StructBlock or StructValue
                    block_replacements = self.process_struct_block(block.value)
                    replacements += block_replacements
                elif isinstance(block.value, dict):  # Dict-like StructBlock
                    block_replacements = self.process_struct_block(block.value)
                    replacements += block_replacements
                elif hasattr(block.value, "__iter__") and not isinstance(
                    block.value, str
                ):  # ListBlock
                    block_replacements = self.process_list_block(block.value)
                    replacements += block_replacements
                elif isinstance(block.value, str):  # String content
                    new_content, block_replacements = self.process_html_content(
                        block.value
                    )
                    if block_replacements > 0:
                        block.value = new_content
                        replacements += block_replacements

        return streamfield, replacements

    def process_struct_block(self, struct_value):
        """Process StructBlock content"""
        replacements = 0

        for key, value in struct_value.items():
            if hasattr(value, "source"):  # RichTextBlock content
                new_content, block_replacements = self.process_html_content(
                    value.source
                )
                if block_replacements > 0:
                    struct_value[key] = value.__class__(new_content)
                    replacements += block_replacements
            elif isinstance(value, RichText):  # RichText content
                new_content, block_replacements = self.process_html_content(str(value))
                if block_replacements > 0:
                    struct_value[key] = RichText(new_content)
                    replacements += block_replacements
            elif isinstance(value, str):  # String content
                new_content, block_replacements = self.process_html_content(value)
                if block_replacements > 0:
                    struct_value[key] = new_content
                    replacements += block_replacements
            elif isinstance(value, dict):
                replacements += self.process_struct_block(value)
            elif isinstance(value, list):
                replacements += self.process_list_block(value)

        return replacements

    def process_list_block(self, list_value):
        """Process ListBlock content"""
        replacements = 0

        for i, item in enumerate(list_value):
            if hasattr(item, "source"):  # RichTextBlock in list
                new_content, block_replacements = self.process_html_content(item.source)
                if block_replacements > 0:
                    list_value[i] = item.__class__(new_content)
                    replacements += block_replacements
            elif hasattr(item, "items"):  # StructValue in list
                replacements += self.process_struct_block(item)
            elif isinstance(item, dict):
                replacements += self.process_struct_block(item)
            elif isinstance(item, list):
                replacements += self.process_list_block(item)
            elif isinstance(item, str):
                new_content, block_replacements = self.process_html_content(item)
                if block_replacements > 0:
                    list_value[i] = new_content
                    replacements += block_replacements

        return replacements

    def process_html_content(self, html_content):
        """Process HTML content and replace PDF links"""
        if not html_content or "<a href=" not in html_content:
            return html_content, 0

        # Pattern to match PDF links: <a href="path/to/file.pdf" ...>text</a>
        pdf_link_pattern = r'<a\s+href="([^"]*\.pdf)"([^>]*)>(.*?)</a>'

        replacements = 0

        def replace_link(match):
            nonlocal replacements

            pdf_url = match.group(1)
            other_attrs = match.group(2)
            link_text = match.group(3)

            # Extract filename from URL
            filename = pdf_url.split("/")[-1]

            # Find document by filename
            document = self.find_document_by_filename(filename)

            if document:
                replacements += 1
                # Track the replacement for logging
                self.page_replacements.append((filename, document.title, document.id))

                # Create new link with document reference
                new_link = f'<a linktype="document" id="{document.id}"{other_attrs}>{link_text}</a>'

                if self.dry_run:
                    self.stdout.write(
                        f"    Would replace: {filename} → Document ID {document.id} ({document.title})"
                    )

                return new_link
            else:
                self.stdout.write(
                    self.style.WARNING(f"    Document not found for: {filename}")
                )
                return match.group(0)  # Return original if document not found

        new_content = re.sub(
            pdf_link_pattern,
            replace_link,
            html_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        return new_content, replacements

    def find_document_by_filename(self, filename):
        """Find Wagtail document by filename"""
        try:
            # Try exact filename match first
            document = self.Document.objects.filter(file__icontains=filename).first()

            if not document:
                # Try without extension
                base_filename = filename.rsplit(".", 1)[0]
                document = self.Document.objects.filter(
                    file__icontains=base_filename
                ).first()

            return document
        except Exception as e:
            logger.warning(f"Error finding document {filename}: {e}")
            return None
