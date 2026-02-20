"""
Management command to create a test page with Table containing all block types.
This is for local testing only. Run with:
    python manage.py create_table_test_page
To delete the test page:
    python manage.py create_table_test_page --delete
"""

from django.core.management.base import BaseCommand
from home.management.commands.pages.table_test_page import TableTestPageInitializer


class Command(BaseCommand):
    help = "Create a test page with Table containing all block types for local testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the test page instead of creating it.",
        )

    def handle(self, *args, **options):
        initializer = TableTestPageInitializer()

        if options["delete"]:
            initializer.delete()
            self.stdout.write(
                self.style.SUCCESS("Table test page deleted (if it existed).")
            )
        else:
            initializer.create()
            self.stdout.write(
                self.style.SUCCESS(
                    "Table test page created. Visit /table-test/ to view it."
                )
            )
