from django.core.management.base import BaseCommand

from app.wagtaillinkchecker.scanner import broken_link_scan
from app.wagtaillinkchecker.models import ScanLink

from wagtail.models import Site


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        site = Site.objects.filter(is_default_site=True).first()
        pages = site.root_page.get_descendants(inclusive=True).live().public()
        verbosity = 2

        print(f"Scanning {len(pages)} pages...")
        scan = broken_link_scan(site, verbosity, sync=True)
        total_links = ScanLink.objects.filter(scan=scan, crawled=True)
        broken_links = ScanLink.objects.filter(scan=scan, broken=True)
        print(
            f"Found {len(total_links)} total links, with {len(broken_links)} broken links."
        )
