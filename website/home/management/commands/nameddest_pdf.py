import os
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from django.core.management.base import BaseCommand


# how to run
# python manage.py nameddest_pdf --pdf_name rules.pdf --destinations Introduction:1 Chapter1:2


class Command(BaseCommand):
    help = "Add named destinations to a PDF file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pdf_name",
            type=str,
            help="Name of the PDF file to modify (e.g., 'rules.pdf')",
            required=True,
        )
        parser.add_argument(
            "--destinations",
            type=str,
            nargs="+",
            help="List of named destinations in format 'name:page' (e.g., 'Introduction:1 Chapter1:2')",
            required=True,
        )

    def handle(self, *args, **kwargs):
        pdf_name = kwargs["pdf_name"]
        destinations = kwargs["destinations"]

        # Get the project root directory
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        pdf_path = os.path.join(BASE_DIR, "management", "commands", pdf_name)
        output_path = os.path.join(
            BASE_DIR, "management", "commands", f"modified_{pdf_name}"
        )

        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f"PDF file not found at: {pdf_path}"))
            return

        try:
            # Read the existing PDF
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Add named destinations
            for dest in destinations:
                try:
                    name, page = dest.split(":")
                    page_num = int(page) - 1  # Convert to 0-based index
                    if page_num < 0 or page_num >= len(reader.pages):
                        self.stdout.write(
                            self.style.ERROR(
                                f"Invalid page number {page} for destination '{name}'"
                            )
                        )
                        continue
                    writer.add_named_destination(name, page_num)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added destination '{name}' for page {page}"
                        )
                    )
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Invalid destination format: {dest}. Use 'name:page' format"
                        )
                    )

            # Save the new PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            self.stdout.write(
                self.style.SUCCESS(f"Modified PDF saved to: {output_path}")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing PDF: {str(e)}"))
