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
    help = (
        "Generate PDF rule redirects from CSV and output CloudFront-safe JS using regex"
    )

    def handle(self, *args, **options):
        self.stdout.write(
            "Starting redirect generation using regex-based CloudFront function..."
        )

        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR("Default Wagtail Site not found."))
            return

        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        csv_path = base_dir / "home" / "migrations" / "0064_update_rules_documents.csv"
        json_output_path = base_dir / "redirects" / "pdf_redirects.json"
        js_output_path = base_dir / "redirects" / "pdf_redirect_function.js"

        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        js_output_path.parent.mkdir(parents=True, exist_ok=True)

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return

        initializer = RedirectInitializer()
        redirects = {}

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                old_path = f"/files/documents/{row['current_filename'].strip()}"
                new_path = f"/files/documents/{row['new_title'].strip()}"

                if old_path == new_path:
                    continue

                redirects[old_path] = new_path
                initializer.create(old_path, new_path, is_permanent=True)

        # Link site to all site-less redirects
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

        # Write full redirect map JSON (for backup or debugging)
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(redirects, f, indent=2)

        # Write CloudFront Function JS with regex-based logic
        js_code = """
        function handler(event) {
          var request = event.request;
          if (request.uri.startsWith('/files/')) {
            request.uri = request.uri.slice(6);
          }

          var uri = request.uri;
          // Exact path redirects
          var redirects = {
            "/files/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf": "/files/documents/Complete-Rules-of-Practice-and-Procedure.pdf",
            "/files/documents/Rule-229A.pdf": "/files/documents/rule-229A.pdf",
            "/files/documents/Rule-2302nd-amended.pdf": "/files/documents/rule-230.pdf",
            "/files/documents/Rule-255.1_amended_08082024.pdf": "/files/documents/rule-255.1.pdf",
            "/files/documents/Rule-255.2New.pdf": "/files/documents/rule-255.2.pdf",
            "/files/documents/Rule-255.3New.pdf": "/files/documents/rule-255.3.pdf",
            "/files/documents/Rule-255.4New.pdf": "/files/documents/rule-255.4.pdf",
            "/files/documents/Rule-255.5New.pdf": "/files/documents/rule-255.5.pdf",
            "/files/documents/Rule-255.6New.pdf": "/files/documents/rule-255.6.pdf",
            "/files/documents/Rule-255.7New.pdf": "/files/documents/rule-255.7.pdf"
          };

          if (redirects[uri]) {
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: redirects[uri].replace("/documents/Rule-", "/documents/rule-") }
              }
            };
          }
          // Regex-based matching
          var pattern = /^\/documents\/Rule-\d+[.\-_A-Za-z0-9]*?(amended|Amended|superseded|2nd|2nd-amended|New|new)[^\/]*\.pdf$/;
          var genericPattern = /^\/documents\/Rule-[\d.]+\.pdf$/;

          if (pattern.test(uri)) {
            var newUri = uri.replace(/^\/documents\/(Rule-\d+)[^\/]*\.pdf$/, "/documents/$1.pdf");
            newUri = newUri.replace("/documents/Rule-", "/documents/rule-"); // lowercase only "Rule"
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: "/files" + newUri }
              }
            };
          }

          if (genericPattern.test(uri)) {
            var newUri = uri.replace("/documents/Rule-", "/documents/rule-"); // lowercase only "Rule"
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: "/files" + newUri }
              }
            };
          }
          return request;
        }
        """.strip()

        with open(js_output_path, "w", encoding="utf-8") as f:
            f.write(js_code)

        size_bytes = js_output_path.stat().st_size
        size_kb = round(size_bytes / 1024, 2)
        if size_bytes > 10240:
            self.stderr.write(
                f"Warning: JS file size is {size_kb} KB (exceeds 10 KB limit)"
            )
        else:
            self.stdout.write(f"JS file generated: {js_output_path} ({size_kb} KB)")

        self.stdout.write(
            self.style.SUCCESS(f"{len(redirects)} total redirects processed")
        )
        self.stdout.write(
            self.style.SUCCESS(f"{updated} existing redirects linked to site")
        )
