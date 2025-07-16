from django.conf import settings
from django.db import migrations
from django.core.files import File
from django.core.exceptions import MultipleObjectsReturned
import os
import csv


# --- Helper Function ---
def update_document_file(
    Document, current_title, base_path, source_filename, new_title
):
    """
    Finds a Wagtail document by its ID, updates its title, and replaces its file
    by uploading a new file from the local filesystem.

    Constructs the full file path from a base path and a source filename.
    """
    full_path = os.path.join(base_path, source_filename)
    try:
        # Get the document object using the provided title.
        # This requires the title to be unique.
        doc_to_update = Document.objects.get(title=current_title)

        print(
            f"Found document by title '{current_title}' (ID: {doc_to_update.id}). Updating..."
        )

        # Update the title field
        doc_to_update.title = new_title

        # Open the new PDF file from the constructed full path
        with open(full_path, "rb") as f:
            # This is the key step. The .save() method on the FileField will
            # use your project's default storage backend. If you have django-storages
            # configured for S3, this line will read the local file and upload
            # it to your S3 bucket, replacing the old file.
            print(
                f"  -> Uploading '{source_filename}' to configured storage (e.g., S3)..."
            )
            doc_to_update.file.save(source_filename, File(f))

        print(
            f"  -> Successfully updated to title '{new_title}' with file '{source_filename}'."
        )

    except Document.DoesNotExist:
        print(f"  -> ERROR: Document with title '{current_title}' not found. Skipping.")
    except MultipleObjectsReturned:
        print(
            f"  -> ERROR: Multiple documents found with title '{current_title}'. Titles must be unique to use this script. Skipping."
        )
    except FileNotFoundError:
        print(
            f"  -> ERROR: Source file not found at '{full_path}'. Skipping document '{current_title}'."
        )
    except Exception as e:
        print(
            f"  -> ERROR: An unexpected error occurred for document '{current_title}': {e}"
        )


def apply_document_updates_from_csv(apps, schema_editor):
    """
    The main migration function. It reads data from a CSV file
    and calls the helper function for each row.
    """
    # It's crucial to get the model from the historical 'apps' registry
    Document = apps.get_model("wagtaildocs", "Document")

    # --- IMPORTANT ---
    # Define the absolute base directory where your new source document files are located.
    # The migration will look for filenames from the CSV inside this directory.
    # PLEASE UPDATE THIS PATH to the correct location on your server.
    BASE_DIR = settings.BASE_DIR
    LOCAL_FILES_BASE_DIR = os.path.join(BASE_DIR, "home/management/documents")
    print(f"Base directory: {BASE_DIR}, full directory: {LOCAL_FILES_BASE_DIR}")

    # Construct the path to the CSV file relative to this migration file
    migration_dir = os.path.dirname(__file__)
    csv_filename = os.path.basename(__file__).replace(
        ".py", ".csv"
    )  # e.g., 0058_rules_document_updates.csv
    csv_path = os.path.join(migration_dir, csv_filename)

    print(f"\nAttempting to read document updates from: {csv_path}")

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)

            # Skip the header row
            header = next(reader)
            print(f"CSV Header found: {header}")

            # Process each row in the CSV
            for row in reader:
                # Expects columns in order: current_title, source_filename, new_title
                current_title, source_filename, new_title = row
                update_document_file(
                    Document,
                    current_title.strip(),
                    LOCAL_FILES_BASE_DIR,
                    source_filename.strip(),
                    new_title.strip(),
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
        ),  # Dependency on wagtaildocs is good practice
    ]

    operations = [
        # This tells Django to run our function when applying the migration.
        # The second argument (migrations.RunPython.noop) means Django does nothing
        # when un-migrating, as these file changes are hard to reverse automatically.
        migrations.RunPython(
            apply_document_updates_from_csv, migrations.RunPython.noop
        ),
    ]
