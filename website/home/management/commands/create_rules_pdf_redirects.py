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
        "Generate PDF rule redirects from CSV and output CloudFront-safe JS + full JSON"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Max redirects for CloudFront Function (default: 100)",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        self.stdout.write(f"Starting redirect generation (limit={limit})")

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
        cloudfront_redirects = {}

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                old_path = f"/files/documents/{row['current_filename'].strip()}"
                new_path = f"/files/documents/{row['new_title'].strip()}"

                if old_path == new_path:
                    continue

                redirects[old_path] = new_path
                if len(cloudfront_redirects) < limit:
                    cloudfront_redirects[old_path] = new_path
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

        # Write full redirect map JSON (for Wagtail debugging or fallback logic)
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(redirects, f, indent=2)

        # Write CloudFront Function JS
        js_lines = [
            "function handler(event) {",
            "  var request = event.request;",
            "  var redirects = {",
        ]
        for i, (src, dst) in enumerate(cloudfront_redirects.items()):
            comma = "," if i < len(cloudfront_redirects) - 1 else ""
            js_lines.append(f'    "{src}": "{dst}"{comma}')
        js_lines += [
            "  };",
            "  if (redirects.hasOwnProperty(request.uri)) {",
            "    return {",
            "      statusCode: 302,",
            '      statusDescription: "Found",',
            "      headers: {",
            "        location: { value: redirects[request.uri] }",
            "      }",
            "    };",
            "  }",
            "  if (request.uri.startsWith('/files/')) {",
            "    request.uri = request.uri.slice(6);",
            "  }",
            "  return request;",
            "}",
        ]
        js_code = "\n".join(js_lines)
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
            self.style.SUCCESS(
                f"{len(cloudfront_redirects)} CloudFront redirects created"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"{len(redirects)} total redirects processed")
        )
        self.stdout.write(
            self.style.SUCCESS(f"{updated} existing redirects linked to site")
        )
