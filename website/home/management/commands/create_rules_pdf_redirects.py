import csv
from pathlib import Path
import logging

from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.contrib.redirects.models import Redirect

from home.management.commands.redirects.redirect_initializer import RedirectInitializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate Wagtail redirects AND CloudFront function JS from CSV"

    def handle(self, *args, **options):
        self.stdout.write("Starting PDF rule redirect creation...")

        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR("Default Wagtail Site not found."))
            return

        initializer = RedirectInitializer()

        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        csv_path = base_dir / "home" / "migrations" / "0060_update_rules_documents.csv"
        output_js = base_dir / "cloudfront" / "pdf_redirect_function.js"

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return

        redirects = {}
        created_count = 0

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)
                if header != ["current_title", "source_filename", "new_title"]:
                    self.stdout.write(
                        self.style.WARNING(f"CSV header mismatch: {header}")
                    )

                for current_title, source_filename, new_title in reader:
                    current_title = current_title.strip()
                    new_title = new_title.strip()

                    # Build the old and new URL paths
                    old_path = f"/files/documents/{current_title}"
                    new_path = f"/files/documents/{new_title}"

                    initializer.create(old_path, new_path)
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

        # Write CloudFront function JS
        output_js.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(output_js, "w") as f:
                f.write("function handler(event) {\n")
                f.write("    var request = event.request;\n")
                f.write("    var redirects = {\n")
                for src, dest in redirects.items():
                    f.write(f'        "{src}": "{dest}",\n')
                f.write("    };\n")
                f.write("    var target = redirects[request.uri];\n")
                f.write("    if (target) {\n")
                f.write("        return {\n")
                f.write("            statusCode: 302,\n")
                f.write('            statusDescription: "Found",\n')
                f.write("            headers: {\n")
                f.write("                location: { value: target }\n")
                f.write("            }\n")
                f.write("        };\n")
                f.write("    }\n")
                f.write("    return request;\n")
                f.write("}\n")

            self.stdout.write(
                self.style.SUCCESS(f"CloudFront function JS written to: {output_js}")
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f" Failed to write CloudFront function JS: {e}")
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} Wagtail redirects.")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Linked {updated} redirects to the default site.")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "All redirects and CloudFront function generated successfully."
            )
        )
