"""
Management command to create a test page with CardTiles containing all block types.

This is for local testing only. Run with:
    python manage.py create_card_tiles_test_page

To delete the test page:
    python manage.py create_card_tiles_test_page --delete
"""

from django.core.management.base import BaseCommand
from home.management.commands.pages.card_tiles_test_page import (
    CardTilesTestPageInitializer,
)


class Command(BaseCommand):
    help = "Create a test page with CardTiles containing all block types for local testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the test page instead of creating it.",
        )

    def handle(self, *args, **options):
        initializer = CardTilesTestPageInitializer()

        if options["delete"]:
            initializer.delete()
            self.stdout.write(
                self.style.SUCCESS("Card Tiles test page deleted (if it existed).")
            )
        else:
            initializer.create()
            self.stdout.write(
                self.style.SUCCESS(
                    "Card Tiles test page created. Visit /card-tiles-test/ to view it."
                )
            )
