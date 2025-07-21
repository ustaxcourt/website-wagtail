from django.conf import settings
from django.db import migrations
from django.core.files import File
from django.core.exceptions import MultipleObjectsReturned
import os
import csv
import logging

logger = logging.getLogger(__name__)

files_to_remove = [
    "Rule-27.pdf",
    "Rule-121.pdf",
    "Rule-74amended.pdf",
    "Rule-81.pdf",
    "Rule-280amended.pdf",
    "Rule-21.pdf",
    "Rule-151.pdf",
    "Rule-147.pdf",
]


def update_document_file(
    Document, current_filename, base_path, source_filename, new_title, collection
):
    """
    Finds a Wagtail document by its filename, updates its title, and replaces its file
    by uploading a new file from the local filesystem.

    Constructs the full file path from a base path and a source filename.
    """
    full_path = os.path.join(base_path, source_filename)
    try:
        # Get the document object using the provided filename.
        doc_to_update = Document.objects.get(file__endswith=current_filename)
        logger.info(
            f"Found document by filename '{current_filename}' (ID: {doc_to_update.id}). Updating..."
        )

        # Update the title field
        doc_to_update.title = new_title
        doc_to_update.collection = collection
        doc_to_update.save(update_fields=["title", "collection"])
        logger.info(
            f"  -> Successfully updated title to '{new_title}' and set collection."
        )

        # Check if the document already exists
        if Document.objects.filter(file=f"documents/{source_filename}").exists():
            logger.info(f"Document of {source_filename} already exists.")
            return

        else:
            # Open the new PDF file from the constructed full path
            with open(full_path, "rb") as f:
                logger.info(
                    f"  -> Uploading '{source_filename}' to configured storage (e.g., S3)..."
                )
                doc_to_update.file.save(source_filename, File(f))

        logger.info(
            f"  -> Successfully updated to title '{new_title}' with file '{source_filename}'."
        )

    except Document.DoesNotExist:
        logger.error(
            f"  -> Document with filename '{current_filename}' not found. Skipping."
        )
    except MultipleObjectsReturned:
        logger.error(
            f"  -> ERROR: Multiple documents found with filename '{current_filename}'. Titles must be unique to use this script. Skipping."
        )
    except FileNotFoundError:
        logger.error(
            f"  -> ERROR: Source file not found at '{full_path}'. Skipping document '{current_filename}'."
        )
    except Exception as e:
        logger.error(
            f"  -> ERROR: An unexpected error occurred for document '{current_filename}': {e}"
        )


def delete_documents_from_list(Document, filenames_to_delete):
    """
    Finds and deletes a list of Wagtail documents by their filenames.

    Args:
        filenames_to_delete (list): A list of document filenames to delete.
    """
    logger.info(
        f"--- Starting bulk deletion of {len(filenames_to_delete)} documents ---"
    )

    # Counters for the summary
    success_count = 0
    not_found_count = 0
    error_count = 0

    for filename in filenames_to_delete:
        try:
            # Get the document object using the provided filename
            doc_to_delete = Document.objects.get(file__endswith=filename)
            doc_id = doc_to_delete.id  # Store ID for logging after deletion

            logger.info(f"Found document '{filename}' (ID: {doc_id}). Deleting...")

            # Delete the document object
            doc_to_delete.delete()

            logger.info(
                f"  -> Successfully deleted document '{filename}' (formerly ID: {doc_id})."
            )
            success_count += 1

        except Document.DoesNotExist:
            logger.warning(
                f"  -> Document with filename '{filename}' not found. Skipping."
            )
            not_found_count += 1
        except MultipleObjectsReturned:
            logger.error(
                f"  -> ERROR: Multiple documents found with filename '{filename}'. "
                f"Cannot determine which to delete. Skipping."
            )
            error_count += 1
        except Exception as e:
            logger.error(
                f"  -> ERROR: An unexpected error occurred for document '{filename}': {e}"
            )
            error_count += 1

    # Log a final summary
    logger.info("--- Bulk deletion process complete ---")
    logger.info(
        f"Summary: {success_count} deleted, {not_found_count} not found, {error_count} failed."
    )


def apply_document_updates_from_csv(apps, schema_editor):
    """
    The main migration function. It reads data from a CSV file
    and calls the helper function for each row.
    """
    # It's crucial to get the model from the historical 'apps' registry
    Document = apps.get_model("wagtaildocs", "Document")
    Collection = apps.get_model("wagtailcore", "Collection")

    # --- IMPORTANT ---
    # The migration will look for filenames from the CSV inside this directory.
    # PLEASE UPDATE THIS PATH to the correct location on your server.
    BASE_DIR = settings.BASE_DIR
    LOCAL_FILES_BASE_DIR = os.path.join(BASE_DIR, "home/management/documents/rules")

    # Construct the path to the CSV file relative to this migration file
    migration_dir = os.path.dirname(__file__)
    csv_filename = os.path.basename(__file__).replace(".py", ".csv")
    update_csv_path = os.path.join(migration_dir, csv_filename)

    logger.info(f"\nAttempting to read document updates from: {update_csv_path}")

    collection_name = "Tax Court Rules"
    try:
        # First, try to get the collection if it already exists.
        collection = Collection.objects.get(name=collection_name)
        logger.info(f"Found existing collection: '{collection_name}'")
    except Collection.DoesNotExist:
        # If the collection doesn't exist, we must use the REAL model to create it
        # because the historical model from apps.get_model lacks the 'add_child' method.
        # This is a known workaround for this specific limitation in data migrations.
        from wagtail.models import Collection as RealCollection

        logger.info(f"Collection '{collection_name}' not found. Creating it...")
        try:
            # Use the real model to get the root and create the child
            root_collection_real = RealCollection.objects.get(depth=1)
            new_collection_real = root_collection_real.add_child(name=collection_name)
            logger.info(f"Created new collection: '{collection_name}'")

            # Now, fetch the newly created collection using the historical model
            # so the rest of the migration can use it.
            collection = Collection.objects.get(pk=new_collection_real.pk)
        except Exception as e:
            logger.error(f"FATAL: Could not create collection. Error: {e}")
            raise

    try:
        with open(update_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)

            # Skip the header row
            header = next(reader)
            logger.info(f"CSV Header found: {header}")

            # Process each row in the CSV
            for row in reader:
                # Expects columns in order: current_filename, source_filename, new_title
                current_filename, source_filename, new_title = row
                update_document_file(
                    Document,
                    current_filename.strip(),
                    LOCAL_FILES_BASE_DIR,
                    source_filename.strip(),
                    new_title.strip(),
                    collection,
                )

    except FileNotFoundError:
        logger.error(
            f"\nFATAL ERROR: The CSV file was not found at '{update_csv_path}'."
        )
        logger.error(
            "Please ensure the CSV is in the same directory as this migration file."
        )
        # We raise an exception to halt the migration process if the file is missing.
        raise
    except Exception as e:
        logger.error(
            f"\nFATAL ERROR: An error occurred while processing the CSV file: {e}"
        )
        raise

    delete_documents_from_list(Document, filenames_to_delete=files_to_remove)


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0059_update_petitioner_start_doc_references"),
        (
            "wagtaildocs",
            "0012_uploadeddocument",
        ),
    ]

    operations = [
        # The second argument (migrations.RunPython.noop) means Django does nothing
        # when un-migrating, as these file changes are hard to reverse automatically.
        migrations.RunPython(
            apply_document_updates_from_csv, migrations.RunPython.noop
        ),
    ]
