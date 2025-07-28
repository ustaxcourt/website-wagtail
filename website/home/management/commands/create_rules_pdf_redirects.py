import csv
import json
from pathlib import Path
import logging

from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.contrib.redirects.models import Redirect

from home.management.commands.redirects.redirect_initializer import RedirectInitializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate PDF rule redirects from CSV using RedirectInitializer and output CloudFront redirect map JSON."

    def handle(self, *args, **options):
        self.stdout.write("Starting PDF rule redirect creation...")

        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR("Default Wagtail Site not found."))
            return

        initializer = RedirectInitializer()

        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        csv_path = base_dir / "home" / "migrations" / "0064_update_rules_documents.csv"
        json_output_path = base_dir / "redirects" / "pdf_redirects.json"
        js_output_path = base_dir / "redirects" / "pdf_redirect_function.js"

        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        js_output_path.parent.mkdir(parents=True, exist_ok=True)

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return

        redirects = {}
        created_count = 0

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)
                expected_header = ["current_filename", "source_filename", "new_title"]
                if header != expected_header:
                    self.stdout.write(
                        self.style.WARNING(f"CSV header mismatch: {header}")
                    )

                for current_filename, source_filename, new_title in reader:
                    current_filename = current_filename.strip()
                    new_title = new_title.strip()

                    # Build the old and new URL paths
                    old_path = f"/files/documents/{current_filename}"
                    new_path = f"/files/documents/{new_title}"

                    if old_path == new_path:
                        continue
                    # Create the redirect using RedirectInitializer
                    initializer.create(old_path, new_path, is_permanent=True)
                    redirects[old_path] = new_path
                    created_count += 1

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing CSV: {e}"))
            return

        updated = 0
        for redirect in Redirect.objects.filter(site__isnull=True):
            redirect.site = site
            redirect.save()
            updated += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Linked site to redirect: {redirect.old_path} → {redirect.redirect_link}"
                )
            )

        # Write JSON
        try:
            with open(json_output_path, "w", encoding="utf-8") as jsonfile:
                json.dump(redirects, jsonfile, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f"Wrote redirect map to {json_output_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to write redirect JSON: {e}"))

        # Write JS Function
        try:
            with open(js_output_path, "w", encoding="utf-8") as f:
                f.write("function handler(event) {\n")
                f.write("  var request = event.request;\n")
                f.write("  var redirects = {\n")
                for i, (src, dest) in enumerate(redirects.items()):
                    comma = "," if i < len(redirects) - 1 else ""
                    f.write(f'    "{src}": "{dest}"{comma}\n')
                f.write("  };\n")
                f.write("  if (redirects.hasOwnProperty(request.uri)) {\n")
                f.write("    return {\n")
                f.write("      statusCode: 302,\n")
                f.write('      statusDescription: "Found",\n')
                f.write("      headers: {\n")
                f.write("        location: { value: redirects[request.uri] }\n")
                f.write("      }\n")
                f.write("    };\n")
                f.write("  }\n")
                f.write("  if (request.uri.startsWith('/files/')) {\n")
                f.write("    request.uri = request.uri.slice(6);\n")
                f.write("  }\n")
                f.write("  return request;\n")
                f.write("}\n")
            self.stdout.write(
                self.style.SUCCESS(f"Wrote CloudFront JS function to {js_output_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to write JS function: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} redirects."))
        self.stdout.write(
            self.style.SUCCESS(f"Linked {updated} redirects to the default site.")
        )
        self.stdout.write(self.style.SUCCESS("All redirects processed successfully."))
