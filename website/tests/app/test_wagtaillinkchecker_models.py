"""Tests for app/wagtaillinkchecker/models.py and app/wagtaillinkchecker/tasks.py"""

import pytest
from unittest.mock import patch, MagicMock
from wagtail.models import Locale, Page, Site
from app.wagtaillinkchecker.models import Scan, ScanLink
from app.wagtaillinkchecker.tasks import check_link_sync

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_site():
    """Return a minimal Wagtail Site backed by a real root Page."""
    Locale.objects.get_or_create(language_code="en")
    root_page = Page.objects.filter(depth=1).first()
    if root_page is None:
        root_page = Page.add_root(title="Root", slug="root")
    site, _ = Site.objects.get_or_create(
        hostname="testserver-linkchecker",
        defaults={
            "root_page": root_page,
            "is_default_site": False,
            "port": 80,
            "site_name": "Test Site",
        },
    )
    return site


def _make_scan(site):
    return Scan.objects.create(site=site)


def _make_scan_link(
    scan, url, *, broken=False, crawled=False, invalid=False, page=None
):
    return ScanLink.objects.create(
        scan=scan,
        url=url,
        broken=broken,
        crawled=crawled,
        invalid=invalid,
        page=page,
    )


# ---------------------------------------------------------------------------
# Scan.is_finished
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestScanIsFinished:
    def test_is_finished_returns_true_when_status_is_completed(self):
        scan = _make_scan(_make_site())
        scan.status = Scan.Status.COMPLETED
        assert scan.is_finished is True

    def test_is_finished_returns_false_when_status_is_running(self):
        scan = _make_scan(_make_site())
        scan.status = Scan.Status.RUNNING
        assert scan.is_finished is False

    def test_is_finished_returns_false_when_status_is_failed(self):
        scan = _make_scan(_make_site())
        scan.status = Scan.Status.FAILED
        assert scan.is_finished is False


# ---------------------------------------------------------------------------
# ScanLinkQuerySet
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestScanLinkQuerySet:
    def _setup(self):
        """Create a scan with a varied set of links covering all flag combinations."""
        scan = _make_scan(_make_site())
        working = _make_scan_link(scan, "https://example.com/working", crawled=True)
        broken = _make_scan_link(
            scan, "https://example.com/broken", broken=True, crawled=True
        )
        uncrawled = _make_scan_link(scan, "https://example.com/uncrawled")
        invalid = _make_scan_link(
            scan, "https://example.com/invalid", invalid=True, crawled=True
        )
        # A link that is both broken and invalid — should NOT appear in broken_links()
        invalid_and_broken = _make_scan_link(
            scan,
            "https://example.com/invalid-broken",
            invalid=True,
            broken=True,
            crawled=True,
        )

        broken_uncrawled = _make_scan_link(
            scan, "https://example.com/broken-uncrawled", broken=True
        )

        return (
            scan,
            working,
            broken,
            uncrawled,
            invalid,
            invalid_and_broken,
            broken_uncrawled,
        )

    def test_valid_excludes_links_marked_invalid(self):
        (
            scan,
            working,
            broken,
            uncrawled,
            invalid,
            invalid_and_broken,
            broken_uncrawled,
        ) = self._setup()
        qs = scan.links.valid()
        assert invalid not in qs
        assert invalid_and_broken not in qs

    def test_valid_includes_non_invalid_links(self):
        scan, working, broken, uncrawled, *_ = self._setup()
        qs = scan.links.valid()
        assert working in qs
        assert broken in qs
        assert uncrawled in qs

    def test_broken_links_returns_only_valid_broken_links(self):
        (
            scan,
            working,
            broken,
            uncrawled,
            invalid,
            invalid_and_broken,
            broken_uncrawled,
        ) = self._setup()
        qs = scan.links.broken_links()
        assert broken in qs
        assert working not in qs
        assert broken_uncrawled in qs

    def test_broken_links_excludes_links_marked_as_invalid(self):
        """broken_links() chains through valid(), so a link with invalid=True is excluded even if broken=True."""
        scan, *_, invalid_and_broken, broken_uncrawled = self._setup()
        qs = scan.links.broken_links()
        assert invalid_and_broken not in qs

    def test_crawled_links_returns_valid_crawled_links(self):
        scan, working, broken, uncrawled, invalid, invalid_and_broken, _ = self._setup()
        qs = scan.links.crawled_links()
        assert working in qs
        assert broken in qs
        assert uncrawled not in qs
        assert invalid not in qs

    def test_invalid_links_returns_only_invalid_links(self):
        (
            scan,
            working,
            broken,
            uncrawled,
            invalid,
            invalid_and_broken,
            broken_uncrawled,
        ) = self._setup()
        qs = scan.links.invalid_links()
        assert invalid in qs
        assert invalid_and_broken in qs
        assert working not in qs
        assert broken not in qs

    def test_working_links_returns_valid_crawled_not_broken(self):
        scan, working, broken, uncrawled, invalid, invalid_and_broken, _ = self._setup()
        qs = scan.links.working_links()
        assert working in qs
        assert broken not in qs
        assert uncrawled not in qs
        assert invalid not in qs

    def test_non_scanned_links_returns_uncrawled_links(self):
        scan, working, broken, uncrawled, *_ = self._setup()
        qs = scan.links.non_scanned_links()
        assert uncrawled in qs
        assert working not in qs
        assert broken not in qs


# ---------------------------------------------------------------------------
# ScanLink.page_is_deleted (no DB needed — pure property logic)
# ---------------------------------------------------------------------------


class TestScanLinkPageIsDeleted:
    def test_page_is_deleted_returns_truthy_slug_when_both_are_set(self):
        # NOTE: page_is_deleted returns `self.page_deleted and self.page_slug`, so when
        # truthy the return value is the slug string, not the boolean True. Tests use
        # truthiness rather than identity to reflect actual behavior.
        link = ScanLink()
        link.page_deleted = True
        link.page_slug = "some-slug"
        assert link.page_is_deleted

    def test_page_is_not_deleted_when_page_deleted_is_false(self):
        link = ScanLink()
        link.page_deleted = False
        link.page_slug = "some-slug"
        assert not link.page_is_deleted

    def test_page_is_not_deleted_when_slug_is_none(self):
        # NOTE: returns None (not False) when slug is absent — see comment above.
        link = ScanLink()
        link.page_deleted = True
        link.page_slug = None
        assert not link.page_is_deleted


# ---------------------------------------------------------------------------
# delete_tag signal
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDeleteTagSignal:
    def _make_child_page(self):
        """Create a live child page that can be deleted to trigger the signal."""
        Locale.objects.get_or_create(language_code="en")
        root = Page.objects.filter(depth=1).first()
        if root is None:
            root = Page.add_root(title="Root", slug="root-signal")
        child = root.add_child(
            instance=Page(title="Test Page", slug="test-page-signal-target")
        )
        return child

    def test_page_delete_marks_related_scan_links_as_page_deleted(self):
        scan = _make_scan(_make_site())
        child = self._make_child_page()
        link = _make_scan_link(scan, "https://example.com/test-page", page=child)

        child.delete()

        link.refresh_from_db()
        assert link.page_deleted is True

    def test_page_delete_stores_slug_on_related_scan_links(self):
        scan = _make_scan(_make_site())
        child = self._make_child_page()
        slug = child.slug
        link = _make_scan_link(scan, "https://example.com/test-page", page=child)

        child.delete()

        link.refresh_from_db()
        assert link.page_slug == slug

    def test_page_delete_does_not_affect_unrelated_scan_links(self):
        scan = _make_scan(_make_site())
        child = self._make_child_page()
        unrelated_link = _make_scan_link(
            scan, "https://example.com/unrelated", page=None
        )

        child.delete()

        unrelated_link.refresh_from_db()
        assert unrelated_link.page_deleted is False


# ---------------------------------------------------------------------------
# check_link_sync (tasks.py)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckLinkSync:
    def test_broken_url_marks_scan_link_as_broken(self):
        scan = _make_scan(_make_site())
        link = _make_scan_link(scan, "https://example.com/broken-page")

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value={
                "error": True,
                "invalid_schema": False,
                "error_message": "Connection refused",
                "status_code": None,
            },
        ):
            check_link_sync(link.pk)

        link.refresh_from_db()
        assert link.broken is True
        assert link.error_text == "Connection refused"
        assert link.crawled is True

    def test_invalid_schema_url_marks_scan_link_as_invalid(self):
        scan = _make_scan(_make_site())
        link = _make_scan_link(scan, "tel:+15551234567")

        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value={"error": False, "invalid_schema": True},
        ):
            check_link_sync(link.pk)

        link.refresh_from_db()
        assert link.invalid is True
        assert link.broken is False
        assert link.crawled is True

    def test_successful_non_page_url_marks_scan_link_as_crawled_not_broken(self):
        """An external URL that returns no error and is not a page URL is simply marked crawled."""
        scan = _make_scan(_make_site())
        link = _make_scan_link(scan, "https://external.com/resource", page=None)

        mock_resp = MagicMock()
        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value={
                "error": False,
                "invalid_schema": False,
                "response": mock_resp,
            },
        ):
            check_link_sync(link.pk)

        link.refresh_from_db()
        assert link.crawled is True
        assert link.broken is False
        assert link.invalid is False

    def test_mark_scan_complete_sets_scan_status_when_all_links_crawled(self):
        scan = _make_scan(_make_site())
        link = _make_scan_link(scan, "https://example.com/only-link", page=None)

        mock_resp = MagicMock()
        with patch(
            "app.wagtaillinkchecker.tasks.get_url",
            return_value={
                "error": False,
                "invalid_schema": False,
                "response": mock_resp,
            },
        ):
            check_link_sync(link.pk, mark_scan_complete=True)

        scan.refresh_from_db()
        assert scan.status == Scan.Status.COMPLETED
        assert scan.scan_finished is not None
