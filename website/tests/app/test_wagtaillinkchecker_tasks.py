"""Tests for app/wagtaillinkchecker/tasks.py

Covers the paths not exercised by test_wagtaillinkchecker_models.py:
  - status_code persistence
  - mark_scan_complete when uncrawled links remain
  - HTML crawling branch (anchors, images, data-href)
  - skipped hrefs (None / '#')
  - no recursive re-check when a discovered link already exists
  - BASE_URL setting overrides site.root_url for domain substitution
"""

import pytest
from django.test import override_settings
from unittest.mock import patch, MagicMock
from wagtail.models import Locale, Page, Site

from app.wagtaillinkchecker.models import Scan, ScanLink
from app.wagtaillinkchecker.tasks import check_link_sync


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_site_with_page(hostname="testserver-lc-tasks"):
    """
    Build:
      depth-1 root
       └─ site_root  (set as Site.root_page)
           └─ child  (has a predictable full_url)

    Returns (site, child).
    """
    Locale.objects.get_or_create(language_code="en")

    depth1 = Page.objects.filter(depth=1).first()
    if depth1 is None:
        depth1 = Page.add_root(title="Root", slug="root-lc-tasks")

    site_root = depth1.add_child(
        instance=Page(title="LC Tasks Site Root", slug=f"{hostname}-root")
    )
    site, _ = Site.objects.get_or_create(
        hostname=hostname,
        defaults={
            "root_page": site_root,
            "is_default_site": False,
            "port": 80,
            "site_name": "LC Tasks Test Site",
        },
    )

    child = site_root.add_child(
        instance=Page(title="LC Tasks Target", slug=f"{hostname}-target")
    )
    return site, child


def _make_scan(site):
    return Scan.objects.create(site=site)


def _make_link(scan, url, *, page=None, crawled=False):
    return ScanLink.objects.create(scan=scan, url=url, page=page, crawled=crawled)


def _ok_result(content=b"<html><body></body></html>", status_code=200):
    """Return a get_url result dict simulating a successful response."""
    resp = MagicMock()
    resp.content = content
    return {
        "error": False,
        "invalid_schema": False,
        "response": resp,
        "status_code": status_code,
    }


# ---------------------------------------------------------------------------
# Status code persistence
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckLinkSyncStatusCode:
    def test_status_code_from_get_url_result_is_saved_on_link(self):
        site, _ = _make_site_with_page()
        link = _make_link(_make_scan(site), "https://external.com/page")

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(status_code=200),
        ):
            check_link_sync(link.pk)

        link.refresh_from_db()
        assert link.status_code == 200

    def test_status_code_is_none_when_key_absent_from_get_url_result(self):
        site, _ = _make_site_with_page()
        link = _make_link(_make_scan(site), "https://external.com/page2")

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value={
                "error": False,
                "invalid_schema": False,
                "response": MagicMock(),
            },
        ):
            check_link_sync(link.pk)

        link.refresh_from_db()
        assert link.status_code is None

    def test_non_200_status_code_is_saved_on_broken_link(self):
        site, _ = _make_site_with_page()
        link = _make_link(_make_scan(site), "https://external.com/gone")

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value={
                "error": True,
                "invalid_schema": False,
                "error_message": "Not Found",
                "status_code": 404,
            },
        ):
            check_link_sync(link.pk)

        link.refresh_from_db()
        assert link.status_code == 404
        assert link.broken is True


# ---------------------------------------------------------------------------
# mark_scan_complete — scan stays RUNNING when uncrawled links remain
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckLinkSyncMarkScanComplete:
    def test_scan_stays_running_when_uncrawled_sibling_links_exist(self):
        site, _ = _make_site_with_page()
        scan = _make_scan(site)
        link_a = _make_link(scan, "https://external.com/a")
        _make_link(scan, "https://external.com/b")  # uncrawled sibling

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(),
        ):
            check_link_sync(link_a.pk, mark_scan_complete=True)

        scan.refresh_from_db()
        assert scan.status == Scan.Status.RUNNING
        assert scan.scan_finished is None

    def test_original_link_is_still_marked_crawled_even_when_scan_not_completed(self):
        site, _ = _make_site_with_page()
        scan = _make_scan(site)
        link_a = _make_link(scan, "https://external.com/a")
        _make_link(scan, "https://external.com/b")  # uncrawled sibling

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(),
        ):
            check_link_sync(link_a.pk, mark_scan_complete=True)

        link_a.refresh_from_db()
        assert link_a.crawled is True


# ---------------------------------------------------------------------------
# HTML crawling branch
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckLinkSyncHtmlCrawling:
    """
    Tests the branch entered when link.url matches the page's full_url.
    The branch parses HTML and creates new ScanLinks for every anchor href,
    image src, and div[data-href] it discovers.
    """

    def _crawl_setup(self, html_content, hostname="testserver-lc-tasks"):
        """
        Build a site + page + scan link configured to enter the HTML crawling
        branch.  link.url == child.full_url so the page-match condition is True.
        Returns (site, scan, link).
        """
        site, child = _make_site_with_page(hostname=hostname)
        page_url = child.full_url
        scan = _make_scan(site)
        link = _make_link(scan, page_url, page=child)
        return site, scan, link

    def test_anchor_href_creates_new_scan_link(self, settings):
        html = b"<html><body><a href='/about/'>About</a></body></html>"
        site, scan, link = self._crawl_setup(html)

        with (
            patch(
                "app.wagtaillinkchecker.tasks.get_url",
                return_value=_ok_result(content=html),
            ),
        ):
            settings.BASE_URL = site.root_url  # noqa: F811 - settings used within check_link_sync() call
            check_link_sync(link.pk)

        assert ScanLink.objects.filter(
            scan=scan, url=site.root_url + "/about/"
        ).exists()

    def test_image_src_creates_new_scan_link(self, settings):
        html = b"<html><body><img src='/images/logo.png'></body></html>"
        site, scan, link = self._crawl_setup(html)

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            settings.BASE_URL = site.root_url  # noqa: F811 - settings used within check_link_sync() call
            check_link_sync(link.pk)

        assert ScanLink.objects.filter(
            scan=scan, url=site.root_url + "/images/logo.png"
        ).exists()

    def test_div_data_href_creates_new_scan_link(self, settings):
        html = b"<html><body><div data-href='/section/'>Section</div></body></html>"
        site, scan, link = self._crawl_setup(html)

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            settings.BASE_URL = site.root_url  # noqa: F811 - settings used within check_link_sync() call
            check_link_sync(link.pk)

        assert ScanLink.objects.filter(
            scan=scan, url=site.root_url + "/section/"
        ).exists()

    def test_multiple_link_types_all_create_scan_links(self, settings):
        html = (
            b"<html><body>"
            b"<a href='/page/'>Link</a>"
            b"<img src='/img/photo.jpg'>"
            b"<div data-href='/data-section/'>Section</div>"
            b"</body></html>"
        )
        site, scan, link = self._crawl_setup(html)

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            settings.BASE_URL = site.root_url  # noqa: F811 - settings used within check_link_sync() call
            check_link_sync(link.pk)

        root = site.root_url
        assert ScanLink.objects.filter(scan=scan, url=root + "/page/").exists()
        assert ScanLink.objects.filter(scan=scan, url=root + "/img/photo.jpg").exists()
        assert ScanLink.objects.filter(scan=scan, url=root + "/data-section/").exists()

    def test_anchor_with_hash_only_href_is_not_crawled(self):
        """clean_url('#', site) returns None — no ScanLink should be created."""
        html = b"<html><body><a href='#'>Skip me</a></body></html>"
        site, scan, link = self._crawl_setup(html)
        initial_count = scan.links.count()

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            check_link_sync(link.pk)

        assert scan.links.count() == initial_count

    def test_anchor_with_no_href_attribute_is_not_crawled(self):
        """An <a> with no href: clean_url(None, site) returns None — no new ScanLink."""
        html = b"<html><body><a>No href here</a></body></html>"
        site, scan, link = self._crawl_setup(html)
        initial_count = scan.links.count()

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            check_link_sync(link.pk)

        assert scan.links.count() == initial_count

    def test_img_with_no_src_attribute_is_not_crawled(self):
        """An <img> with no src: clean_url(None, site) returns None — no new ScanLink."""
        html = b"<html><body><img alt='decorative'></body></html>"
        site, scan, link = self._crawl_setup(html)
        initial_count = scan.links.count()

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            check_link_sync(link.pk)

        assert scan.links.count() == initial_count

    def test_existing_scan_link_is_not_rechecked_recursively(self):
        """
        When get_or_create returns created=False (link already in DB),
        check_link_sync must NOT recurse for that link — get_url is called
        exactly once (for the original page link only).
        """
        html = b"<html><body><a href='/existing/'>Existing</a></body></html>"
        site, scan, link = self._crawl_setup(html)

        existing_url = site.root_url + "/existing/"
        existing_link = _make_link(scan, existing_url)  # pre-existing

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ) as mock_get_url:
            check_link_sync(link.pk)

        assert mock_get_url.call_count == 1
        existing_link.refresh_from_db()
        assert existing_link.crawled is False  # untouched

    def test_newly_discovered_links_are_recursively_crawled(self, settings):
        """
        A link discovered during HTML crawling (created=True) gets a recursive
        check_link_sync call, so get_url is called a second time for it.
        """
        html = b"<html><body><a href='/new-page/'>New</a></body></html>"
        site, scan, link = self._crawl_setup(html)

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ) as mock_get_url:
            settings.BASE_URL = site.root_url  # noqa: F811 - settings used within check_link_sync() call
            check_link_sync(link.pk)

        # Once for the original page, once for the discovered /new-page/ link.
        assert mock_get_url.call_count == 2
        new_link = ScanLink.objects.get(scan=scan, url=site.root_url + "/new-page/")
        assert new_link.crawled is True


# ---------------------------------------------------------------------------
# BASE_URL setting overrides site.root_url
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckLinkSyncBaseUrlSetting:
    def test_base_url_is_used_for_domain_substitution_instead_of_site_root_url(self):
        """
        When settings.BASE_URL is set, discovered link URLs are stored with the
        BASE_URL prefix rather than site.root_url.
        """
        site, child = _make_site_with_page(hostname="testserver-lc-tasks-baseurl")
        scan = _make_scan(site)
        base_url = "https://custom-domain.example.com"

        # The tasks module computes domain_name = BASE_URL and checks:
        # link.page.full_url.replace(site.root_url, domain_name) == link.url
        # So we store the link with the BASE_URL prefix to enter the crawling branch.
        page_url_with_base = child.full_url.replace(site.root_url, base_url)
        link = ScanLink.objects.create(scan=scan, url=page_url_with_base, page=child)

        html = b"<html><body><a href='/found/'>Found</a></body></html>"

        with (
            patch(
                "app.wagtaillinkchecker.tasks.get_url",
                return_value=_ok_result(content=html),
            ),
            override_settings(BASE_URL=base_url),
        ):
            check_link_sync(link.pk)

        # Discovered link is stored under BASE_URL, not site.root_url.
        assert ScanLink.objects.filter(scan=scan, url=base_url + "/found/").exists()
        assert not ScanLink.objects.filter(
            scan=scan, url=site.root_url + "/found/"
        ).exists()

    def test_without_base_url_setting_site_root_url_is_used(self, settings):
        """
        When BASE_URL is not configured, site.root_url is the domain used for
        both matching and storing discovered link URLs.
        """
        site, child = _make_site_with_page(hostname="testserver-lc-tasks-nobase")
        scan = _make_scan(site)
        link = _make_link(scan, child.full_url, page=child)

        html = b"<html><body><a href='/found/'>Found</a></body></html>"

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value=_ok_result(content=html),
        ):
            settings.BASE_URL = site.root_url  # noqa: F811 - settings used within check_link_sync() call
            check_link_sync(link.pk)

        assert ScanLink.objects.filter(
            scan=scan, url=site.root_url + "/found/"
        ).exists()
