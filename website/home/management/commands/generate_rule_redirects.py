import os
import re
from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.contrib.redirects.models import Redirect
from home.management.commands.redirects.redirect_initializer import RedirectInitializer


class Command(BaseCommand):
    help = "Generate redirects from legacy rule PDFs to new rule naming convention, and rename Rule-X.pdf to lowercase."

    def handle(self, *args, **options):
        RULES_DIR = os.getenv("RULE_PDF_SCAN_PATH", "home/management/documents")
        amended_pattern = re.compile(r"^(Rule-\d+)_Amended_\d{8}\.pdf$", re.IGNORECASE)
        simple_rule_pattern = re.compile(r"^(Rule-\d+)\.pdf$", re.IGNORECASE)

        redirects = []

        if not os.path.exists(RULES_DIR):
            self.stdout.write(self.style.WARNING(f"Directory not found: {RULES_DIR}"))
            return

        self.stdout.write(f"Scanning directory: {RULES_DIR}\n")

        for filename in os.listdir(RULES_DIR):
            file_path = os.path.join(RULES_DIR, filename)

            # Rule-X_Amended_YYYYMMDD.pdf → rule-x.pdf
            amended_match = amended_pattern.match(filename)
            if amended_match:
                base_rule = amended_match.group(1).lower()
                old_path = f"/files/documents/{filename}"
                new_path = f"/files/documents/{base_rule}.pdf"
                redirects.append(
                    {
                        "old_path": old_path,
                        "new_path": new_path,
                        "is_permanent": True,
                    }
                )
                continue

            # Rule-X.pdf → rule-x.pdf
            simple_match = simple_rule_pattern.match(filename)
            if simple_match:
                base_rule = simple_match.group(1)
                lowercase_name = f"{base_rule.lower()}.pdf"
                new_file_path = os.path.join(RULES_DIR, lowercase_name)

                if filename != lowercase_name:
                    if not os.path.exists(new_file_path):
                        os.rename(file_path, new_file_path)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Renamed: {filename} → {lowercase_name}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipped rename (already exists): {lowercase_name}"
                            )
                        )

                old_path = f"/files/documents/{filename}"
                new_path = f"/files/documents/{lowercase_name}"
                redirects.append(
                    {
                        "old_path": old_path,
                        "new_path": new_path,
                        "is_permanent": True,
                    }
                )

        if not redirects:
            self.stdout.write(self.style.WARNING("No matching rule files found."))
            return

        initializer = RedirectInitializer()
        site = Site.objects.get(is_default_site=True)

        for redirect in redirects:
            initializer.create_redirect(
                redirect["old_path"],
                redirect["new_path"],
                redirect["is_permanent"],
            )

            # Assign redirect to default site
            redirect_obj = Redirect.objects.get(old_path=redirect["old_path"])
            redirect_obj.site = site
            redirect_obj.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created redirect: {redirect['old_path']} → {redirect['new_path']}"
                )
            )

        self.stdout.write(self.style.SUCCESS("✔ Rule redirects and renames completed."))
