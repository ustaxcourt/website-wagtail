"""
Management command to create a test page with components containing external links.
This is for local testing only. Run with:
    python manage.py create_external_links_report_test_page
To delete the test page:
    python manage.py create_external_links_report_test_page --delete
"""

from django.core.management.base import BaseCommand
from home.management.commands.pages.external_links_report_test_page import (
    ExternalLinksReportTestPageInitializer,
)


class Command(BaseCommand):
    help = "Create a test page with components containing external links for local testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the test page instead of creating it.",
        )

    def handle(self, *args, **options):
        initializer = ExternalLinksReportTestPageInitializer()

        if options["delete"]:
            initializer.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    "External Links Report test page deleted (if it existed)."
                )
            )
        else:
            initializer.create()
            self.stdout.write(
                self.style.SUCCESS(
                    "External Links Report test page created. Visit /external-links-report-test/ to view it."
                )
            )
