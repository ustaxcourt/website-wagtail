# path: home/management/commands/generate_rule_redirects.py

import logging
from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.contrib.redirects.models import Redirect
from home.management.commands.redirects.redirect_initializer import RedirectInitializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run PDF rule redirects using RedirectInitializer."

    def handle(self, *args, **options):
        self.stdout.write("📄 Starting PDF rule redirect creation...")

        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR("Default Wagtail Site not found."))
            return

        initializer = RedirectInitializer()
        initializer.create_redirect()  # Uses all logic from redirect_initializer.py

        # Link redirects to the default site if missing
        updated = 0
        for redirect in Redirect.objects.filter(site__isnull=True):
            redirect.site = site
            redirect.save()
            updated += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"✔ Linked site to redirect: {redirect.old_path} -> {redirect.redirect_link}"
                )
            )

        self.stdout.write(self.style.SUCCESS("All redirects processed."))
