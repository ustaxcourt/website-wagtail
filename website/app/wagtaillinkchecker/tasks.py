from background_task import background
from .scanner import get_url, clean_url
from .models import Scan, ScanLink
from bs4 import BeautifulSoup
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone


@background(schedule=5)
def check_link(link_pk, verbosity=1, get_full_result=True):
    return check_link_sync(
        link_pk,
        verbosity=verbosity,
        get_full_result=get_full_result,
        mark_scan_complete=True,
    )


def check_link_sync(
    link_pk, verbosity=1, get_full_result=True, mark_scan_complete=False
):
    link = ScanLink.objects.get(pk=link_pk)
    site = link.scan.site
    domain_name = getattr(settings, "BASE_URL", site.root_url)
    url = get_url(link.url, link.page, site, get_full_result)
    link.status_code = url.get("status_code")

    if url["error"]:
        link.broken = True
        link.error_text = url["error_message"]

    elif url["invalid_schema"]:
        link.invalid = True
        link.error_text = _("Link was invalid")

    elif link.page.full_url.replace(site.root_url, domain_name) == link.url:
        soup = BeautifulSoup(url["response"].content, "html5lib")
        anchors = soup.find_all("a")
        images = soup.find_all("img")

        for anchor in anchors:
            link_href = anchor.get("href")
            link_href = clean_url(link_href, site)
            if verbosity > 1:
                print(f"cleaned link_href: {link_href}")
            if link_href:
                link_href = link_href.replace(site.root_url, domain_name)
                new_link, created = ScanLink.objects.get_or_create(
                    scan=link.scan, url=link_href, defaults={"page": link.page}
                )
                if created:
                    check_link_sync(
                        new_link.pk,
                        verbosity=verbosity,
                        get_full_result=False,
                        mark_scan_complete=mark_scan_complete,
                    )

        for image in images:
            image_src = image.get("src")
            image_src = clean_url(image_src, site)
            if verbosity > 1:
                print(f"cleaned image_src: {image_src}")
            if image_src:
                image_src = image_src.replace(site.root_url, domain_name)
                new_link, created = ScanLink.objects.get_or_create(
                    scan=link.scan, url=image_src, defaults={"page": link.page}
                )
                if created:
                    check_link_sync(
                        new_link.pk,
                        verbosity=verbosity,
                        get_full_result=False,
                        mark_scan_complete=mark_scan_complete,
                    )
    link.crawled = True
    link.save()

    if mark_scan_complete and not link.scan.links.non_scanned_links().exists():
        scan = link.scan
        scan.scan_finished = timezone.now()
        scan.status = Scan.Status.COMPLETED
        scan.save()
