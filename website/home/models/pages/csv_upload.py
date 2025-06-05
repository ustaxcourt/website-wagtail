from home.models.pages.enhanced_standard import EnhancedStandardPage
from django.db import models
from wagtail.admin.panels import FieldPanel


class CSVUploadPage(EnhancedStandardPage):
    csv_file = models.FileField(upload_to="csv_files/")

    content_panels = EnhancedStandardPage.content_panels + [
        FieldPanel("csv_file"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if self.csv_file:
            csv_data = self.get_csv_data()
            if csv_data["headers"] and csv_data["rows"]:
                context["csv_data"] = csv_data
            else:
                context["csv_data"] = None  # Explicitly set to None if no data
        else:
            context["csv_data"] = None
        return context

    def get_csv_data(self):
        import csv
        from io import StringIO

        csv_data = {"headers": [], "rows": []}

        # Open the file and read it
        with self.csv_file.open("r") as file:
            content = file.read()
        if isinstance(content, bytes):  # Check if data is in bytes
            content = content.decode("utf-8")  # Decode bytes to string
        csv_file = StringIO(content)

        # Parse the CSV
        csv_reader = csv.reader(csv_file)

        # Get headers from the first row
        try:
            csv_data["headers"] = next(csv_reader)
            csv_data["rows"] = [row for row in csv_reader]
        except StopIteration:
            # Handle empty CSV
            pass
        finally:
            pass
        return csv_data
