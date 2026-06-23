from http import client

import requests
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from . import HTTP_STATUS_CODES
import logging

logger = logging.getLogger(__name__)


class Link(Exception):
    def __init__(self, url, page, status_code=None, error=None, site=None):
        self.url = url
        self.status_code = status_code
        self.error = error
        self.site = site
        self.page = page

    @property
    def message(self):
        if self.error:
            return self.error
        elif self.status_code in range(100, 300):
            message = "Success"
        elif self.status_code in range(500, 600) and self.url.startswith(
            self.site.root_url
        ):
            message = (
                str(self.status_code)
                + ": "
                + _("Internal server error, please notify the site administrator.")
            )
        else:
            try:
                message = (
                    str(self.status_code)
                    + ": "
                    + client.responses[self.status_code]
                    + "."
                )
            except KeyError:
                message = str(self.status_code) + ": " + _("Unknown error.")
        return message

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; USTaxCourtLinkChecker/1.0; +https://ustaxcourt.gov)"
    )
}


def get_url(url, page, site, get_full_result):
    data = {
        "url": url,
        "page": page,
        "site": site,
        "error": False,
        "invalid_schema": False,
    }
    response = None
    try:
        if get_full_result:
            response = requests.get(url, verify=True, headers=HEADERS, timeout=10)
        else:
            response = requests.head(
                url, verify=True, allow_redirects=True, headers=HEADERS, timeout=10
            )
        data["response"] = response
    except (requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema):
        if not get_full_result:
            return get_url(url, page, site, True)
        data["invalid_schema"] = True
        return data
    except requests.exceptions.ConnectionError:
        if not get_full_result:
            return get_url(url, page, site, True)
        data["error"] = True
        data["error_message"] = _("There was an error connecting to this site")
        return data
    except requests.exceptions.RequestException as e:
        if not get_full_result:
            return get_url(url, page, site, True)
        data["error"] = True
        data["status_code"] = getattr(response, "status_code", None)
        data["error_message"] = type(e).__name__ + ": " + str(e)
        return data

    else:
        if response.status_code not in range(100, 400):
            if not get_full_result:
                return get_url(url, page, site, True)
            error_message_for_status_code = HTTP_STATUS_CODES.get(response.status_code)
            data["error"] = True
            data["status_code"] = response.status_code
            if error_message_for_status_code:
                data["error_message"] = error_message_for_status_code[0]
            else:
                if response.status_code in range(400, 500):
                    data["error_message"] = "Client error"
                elif response.status_code in range(500, 600):
                    data["error_message"] = "Server Error"
                else:
                    data["error_message"] = (
                        "Error: Unknown HTTP Status Code '{0}'".format(
                            response.status_code
                        )
                    )
        return data


def clean_url(url, site):
    if url and url != "#":
        if url.startswith("/"):
            url = site.root_url + url
    else:
        return None
    return url


def broken_link_scan(site, verbosity=1, sync=False):
    from app.wagtaillinkchecker.models import Scan, ScanLink

    pages = site.root_page.get_descendants(inclusive=True).live().public()
    scan = Scan.objects.create(site=site)

    domain_name = getattr(settings, "BASE_URL", site.root_url)

    try:
        for page in pages:
            url = page.full_url.replace(site.root_url, domain_name)
            if verbosity > 1:
                logger.info(f"Checking {url}")
            link, created = ScanLink.objects.get_or_create(
                url=url, scan=scan, defaults={"page": page}
            )
            if created:
                link.check_link(verbosity=verbosity, sync=sync)
            elif link.page_id != page.pk:
                # URL was already discovered as a link from another page, so its
                # HTML was never crawled. Fix the page reference and crawl it now.
                link.page = page
                link.save(update_fields=["page"])
                link.check_link(verbosity=verbosity, sync=sync)
    except Exception:
        scan.status = Scan.Status.FAILED
        scan.save()
        raise

    if sync:
        scan.scan_finished = timezone.now()
        scan.status = Scan.Status.COMPLETED
        scan.save()

    return scan
