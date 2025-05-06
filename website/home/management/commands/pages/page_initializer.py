from abc import ABC, abstractmethod
import os
from wagtail.documents import get_document_model
from wagtail.models import Collection, CollectionViewRestriction
from wagtail.images import get_image_model
from django.core.files import File
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PageInitializer(ABC):
    DOCUMENTS_BASE_PATH = "home/management/documents"
    IMAGES_BASE_PATH = "home/management/images"

    def __init__(self):
        pass

    @abstractmethod
    def create(self):
        pass

    def get_or_create_collection_with_login_restriction(
        self,
        collection_name: str,
        restriction_type: str = "none",  # Add restriction_type parameter
    ) -> Collection:
        """
        Ensures a collection with the given name exists, and that it is restricted
        based on the restriction_type. Returns the collection instance.
        """
        # Get the root collection (top-level)
        root_collection = Collection.get_first_root_node()

        if not collection_name:
            return root_collection

        # See if there's an existing collection by that name
        collection = Collection.objects.filter(name=collection_name).first()
        if not collection:
            # Create a new child collection under the root
            collection = root_collection.add_child(name=collection_name)

        # Ensure it has the specified restriction
        if restriction_type is None:
            restriction_type = "none"  # Set default restriction type if None

        restriction = CollectionViewRestriction.objects.filter(
            collection=collection, restriction_type=restriction_type
        )
        if not restriction.exists():
            # If there's no existing restriction, create one
            CollectionViewRestriction.objects.create(
                collection=collection,
                restriction_type=restriction_type,
            )

        return collection

    def load_document_from_documents_dir(
        self, subdirectory, filename, title=None, collection=None, restriction_type=None
    ):
        """
        Load a document from the documents directory and create a Wagtail Document instance.

        Args:
            subdirectory (str): Subdirectory under DOCUMENTS_BASE_PATH
            filename (str): Name of the file to load
            title (str, optional): Title for the document. If None, uses filename without extension

        Returns:
            Document: The created document instance or None if file not found or already exists
        """
        if subdirectory:
            file_path = os.path.join(
                settings.BASE_DIR, self.DOCUMENTS_BASE_PATH, subdirectory, filename
            )
        else:
            file_path = os.path.join(
                settings.BASE_DIR, self.DOCUMENTS_BASE_PATH, filename
            )

        if not os.path.exists(file_path):
            logger.warning(f"Document file not found at {file_path}")
            return None

        if title is None:
            # Use filename without extension as title
            title = os.path.splitext(filename)[0].replace("_", " ")

        Document = get_document_model()

        # Check if the document already exists
        if Document.objects.filter(title=title).exists():
            logger.info(f"Document with title '{title}' already exists.")
            document = Document.objects.get(title=title)
            print(document.file.url)
            return Document.objects.get(title=title)

        collection_obj = self.get_or_create_collection_with_login_restriction(
            collection, restriction_type
        )

        with open(file_path, "rb") as doc_file:
            document = Document(
                title=title,
                file=File(doc_file, name=filename),
                collection=collection_obj,
            )
            document.save()
            logger.debug(f"Document created: {document}")
            return document

    def load_image_from_images_dir(self, subdirectory, filename, title=None):
        """
        Load an image from the images directory and create a Wagtail Image instance.

        Args:
            subdirectory (str): Subdirectory under IMAGES_BASE_PATH
            filename (str): Name of the file to load
            title (str, optional): Title for the image. If None, uses filename without extension

        Returns:
            Image: The created image instance or None if file not found
        """
        file_path = os.path.join(
            settings.BASE_DIR, self.IMAGES_BASE_PATH, subdirectory, filename
        )

        if not os.path.exists(file_path):
            logger.warning(f"Image file not found at {file_path}")
            return None

        if title is None:
            # Use filename without extension as title
            title = os.path.splitext(filename)[0].replace("_", " ")

        Image = get_image_model()
        if Image.objects.filter(title=title).exists():
            logger.warning(
                f"Image file already exists: {filename}. Choose a different file or title."
            )
            return Image.objects.get(title=title)

        with open(file_path, "rb") as image_file:
            image = Image(
                title=title,
                file=File(image_file, name=filename),
            )
            image.save()
            logger.debug(f"Image created: {image}")
            return image
