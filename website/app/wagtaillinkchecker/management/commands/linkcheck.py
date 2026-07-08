from django.core.management.base import BaseCommand

from app.wagtaillinkchecker.scanner import broken_link_scan
from app.wagtaillinkchecker.models import ScanLink, Scan

from wagtail.models import Site
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--override_setting",
            action="store_true",
            help="Forces a link check scan to initialize if a scan is not running, regardless of environment setting.",
        )
        pass

    def handle(self, *args, **options):
        setting_link_check_enabled = getattr(settings, "LINK_CHECK_ENABLED", False)
        if setting_link_check_enabled or options["override_setting"]:
            site = Site.objects.filter(is_default_site=True).first()
            if not site:
                logger.error("No default Wagtail Site found; aborting linkcheck.")
                return
            if Scan.objects.filter(site=site, status=Scan.Status.RUNNING).exists():
                logger.error(
                    f"A Link Check Scan for Wagtail Site '{site.site_name}' is currently running; aborting linkcheck."
                )
                return
            pages = site.root_page.get_descendants(inclusive=True).live().public()
            verbosity = 2

            logger.info(f"Scanning {pages.count()} pages...")
            scan = broken_link_scan(site, verbosity, sync=True)
            total_links = ScanLink.objects.filter(scan=scan, crawled=True)
            broken_links = ScanLink.objects.filter(scan=scan, broken=True)
            logger.info(
                f"Found {len(total_links)} total links, with {len(broken_links)} broken links."
            )
        else:
            logger.info(
                "Settings prevent a Link Check Scan from starting; aborting linkcheck."
            )
