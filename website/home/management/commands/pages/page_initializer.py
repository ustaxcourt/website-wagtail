from abc import ABC, abstractmethod
import os
from wagtail.documents import get_document_model
from django.core.files import File


class PageInitializer(ABC):
    DOCUMENTS_BASE_PATH = "home/management/documents"

    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def create(self):
        pass

    def load_document_from_documents_dir(self, subdirectory, filename, title=None):
        """
        Load a document from the documents directory and create a Wagtail Document instance.

        Args:
            subdirectory (str): Subdirectory under DOCUMENTS_BASE_PATH
            filename (str): Name of the file to load
            title (str, optional): Title for the document. If None, uses filename without extension

        Returns:
            Document: The created document instance or None if file not found
        """
        file_path = os.path.join(self.DOCUMENTS_BASE_PATH, subdirectory, filename)

        if not os.path.exists(file_path):
            self.logger.write(f"Document file not found at {file_path}")
            return None

        if title is None:
            # Use filename without extension as title
            title = os.path.splitext(filename)[0].replace("_", " ")

        Document = get_document_model()
        with open(file_path, "rb") as doc_file:
            document = Document(
                title=title,
                file=File(doc_file, name=filename),
            )
            document.save()
            return document
