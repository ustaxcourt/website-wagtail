import csv
from pathlib import Path
import logging

from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.contrib.redirects.models import Redirect

from home.management.commands.redirects.redirect_initializer import RedirectInitializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate PDF rule redirects from CSV using RedirectInitializer"

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

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return

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
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} redirects."))
        self.stdout.write(
            self.style.SUCCESS(f"Linked {updated} redirects to the default site.")
        )
        self.stdout.write(self.style.SUCCESS("All redirects processed successfully."))
