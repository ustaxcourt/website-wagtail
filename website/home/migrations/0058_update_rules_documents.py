from django.conf import settings
from django.db import migrations
from django.core.files import File
from django.core.exceptions import MultipleObjectsReturned
import os
import csv


# --- Helper Function ---
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
        print(
            f"Found document by filename '{current_filename}' (ID: {doc_to_update.id}). Updating..."
        )

        # Update the title field
        doc_to_update.title = new_title
        doc_to_update.collection = collection

        # Open the new PDF file from the constructed full path
        with open(full_path, "rb") as f:
            print(
                f"  -> Uploading '{source_filename}' to configured storage (e.g., S3)..."
            )
            doc_to_update.file.save(source_filename, File(f))

        print(
            f"  -> Successfully updated to title '{new_title}' with file '{source_filename}'."
        )

    except Document.DoesNotExist:
        print(
            f"  -> Document with filename '{current_filename}' not found. Skipping."
        )
    except MultipleObjectsReturned:
        print(
            f"  -> ERROR: Multiple documents found with filename '{current_filename}'. Titles must be unique to use this script. Skipping."
        )
    except FileNotFoundError:
        print(
            f"  -> ERROR: Source file not found at '{full_path}'. Skipping document '{current_filename}'."
        )
    except Exception as e:
        print(
            f"  -> ERROR: An unexpected error occurred for document '{current_filename}': {e}"
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
    csv_path = os.path.join(migration_dir, csv_filename)

    print(f"\nAttempting to read document updates from: {csv_path}")

    collection_name = "Tax Court Rules"
    try:
        # First, try to get the collection if it already exists.
        collection = Collection.objects.get(name=collection_name)
        print(f"Found existing collection: '{collection_name}'")
    except Collection.DoesNotExist:
        # If the collection doesn't exist, we must use the REAL model to create it
        # because the historical model from apps.get_model lacks the 'add_child' method.
        # This is a known workaround for this specific limitation in data migrations.
        from wagtail.models import Collection as RealCollection

        print(f"Collection '{collection_name}' not found. Creating it...")
        try:
            # Use the real model to get the root and create the child
            root_collection_real = RealCollection.objects.get(depth=1)
            new_collection_real = root_collection_real.add_child(name=collection_name)
            print(f"Created new collection: '{collection_name}'")

            # Now, fetch the newly created collection using the historical model
            # so the rest of the migration can use it.
            collection = Collection.objects.get(pk=new_collection_real.pk)
        except Exception as e:
            print(f"FATAL: Could not create collection. Error: {e}")
            raise

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)

            # Skip the header row
            header = next(reader)
            print(f"CSV Header found: {header}")

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
        print(f"\nFATAL ERROR: The CSV file was not found at '{csv_path}'.")
        print("Please ensure the CSV is in the same directory as this migration file.")
        # We raise an exception to halt the migration process if the file is missing.
        raise
    except Exception as e:
        print(f"\nFATAL ERROR: An error occurred while processing the CSV file: {e}")
        raise


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0057_fix_petitioner_about_page"),
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
