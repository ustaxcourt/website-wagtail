from django.core.management.base import BaseCommand
from home.management.commands.pages.efiling_and_case_maintenance import (
    efiling_and_case_maintenance_pages_to_update,
)
from home.management.commands.pages.about_the_court import (
    about_the_court_pages_to_update,
)
from home.management.commands.pages.home_page import HomePageInitializer
from home.management.commands.pages.footer import FooterInitializer
from home.management.commands.pages.navigation import NavigationInitializer

from wagtail.documents.models import Document
from wagtail.images.models import Image

# Ensure Home Page is initialized first
pages_to_update = (
    about_the_court_pages_to_update
    + efiling_and_case_maintenance_pages_to_update
    + [FooterInitializer, NavigationInitializer, HomePageInitializer]
)


def create_file_hash_for_documents():
    """Backwards migration: create file hashes for documents if missing."""
    for doc in Document.objects.filter(file_hash=""):
        print(f"Generating file hash for document id={doc.id} name='{doc.title}'")
        doc._set_file_hash()
        doc.save(update_fields=["file_hash"])


def create_file_hash_for_images():
    """Backwards migration: create file hashes for images if missing."""
    for img in Image.objects.filter(file_hash=""):
        print(f"Generating file hash for image id={img.id} name='{img.title}'")
        img._set_file_hash()
        img.save(update_fields=["file_hash"])


class Command(BaseCommand):
    help = "Handle updates to pages and other content."

    def handle(self, *args, **options):
        for page_class in pages_to_update:
            page_instance = page_class()
            page_instance.run()

        self.stdout.write(self.style.SUCCESS("All pages have been updated."))

        create_file_hash_for_documents()
        create_file_hash_for_images()
