import logging
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

from home.management.commands.pages.rules_and_guidance import (
    PetitionersGuidancePageInitializer,
    PetitionersFormsPageInitializer,
    PetitionersPrepareToFilePageInitializer,
    PetitionersTimelinePageInitializer,
    PetitionersHelpPageInitializer,
)

# Ensure Home Page is initialized first
pages_to_update = (
    about_the_court_pages_to_update
    + efiling_and_case_maintenance_pages_to_update
    + [FooterInitializer, NavigationInitializer, HomePageInitializer]
    + [
        PetitionersGuidancePageInitializer,
        PetitionersFormsPageInitializer,
        PetitionersPrepareToFilePageInitializer,
        PetitionersTimelinePageInitializer,
        PetitionersHelpPageInitializer,
    ]
)


def create_file_hash_for_documents():
    """Create file hashes for documents if missing."""
    logger = logging.getLogger(__name__)

    for doc in Document.objects.filter(file_hash=""):
        logger.info(f"Generating file hash for document id={doc.id} name='{doc.title}'")
        """The below method implicitly sets the file's hash if it is empty when it is called."""
        doc.get_file_hash()


def create_file_hash_for_images():
    """Create file hashes for images if missing."""
    logger = logging.getLogger(__name__)

    for img in Image.objects.filter(file_hash=""):
        logger.info(f"Generating file hash for image id={img.id} name='{img.title}'")
        """The below method implicitly sets the image's hash if it is empty when it is called."""
        img.get_file_hash()


class Command(BaseCommand):
    help = "Handle updates to pages and other content."

    def handle(self, *args, **options):
        for page_class in pages_to_update:
            page_instance = page_class()
            page_instance.run()

        self.stdout.write(self.style.SUCCESS("All pages have been updated."))

        create_file_hash_for_documents()
        create_file_hash_for_images()
