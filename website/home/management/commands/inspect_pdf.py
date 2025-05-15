import os
from pathlib import Path
from PyPDF2 import PdfReader
from django.core.management.base import BaseCommand


# how to run
# python manage.py inspect_pdf --pdf_name rules.pdf


class Command(BaseCommand):
    help = "Inspect a PDF file for named destinations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pdf_name",
            type=str,
            help="Name of the PDF file to inspect (e.g., 'Application_for_Waiver_of_Filing_Fee.pdf')",
            required=True,
        )

    def handle(self, *args, **kwargs):
        pdf_name = kwargs["pdf_name"]

        # Get the project root directory
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        pdf_path = os.path.join(BASE_DIR, "management", "commands", pdf_name)

        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f"PDF file not found at: {pdf_path}"))
            return

        try:
            reader = PdfReader(pdf_path)
            destinations = reader._get_named_destinations()

            if destinations:
                self.stdout.write(
                    self.style.SUCCESS(f"Found {len(destinations)} named destinations:")
                )
                for name, dest in destinations.items():
                    self.stdout.write(f"- {name}")
            else:
                self.stdout.write(
                    self.style.WARNING("No named destinations found in the PDF")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading PDF: {str(e)}"))
