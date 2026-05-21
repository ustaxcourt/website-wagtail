"""Tests for home/management/commands/update_search.py"""

import pytest
from io import StringIO
from unittest.mock import MagicMock
from wagtail.models import Locale, Page
from home.management.commands.update_search import Command


@pytest.fixture
def root_page(db):
    Locale.objects.get_or_create(language_code="en")
    return Page.add_root(title="Root", slug="root")


def _make_cmd():
    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()
    cmd.style = MagicMock()
    cmd.style.WARNING = lambda s: s
    cmd.style.ERROR = lambda s: s
    cmd.style.SUCCESS = lambda s: s
    cmd.style.HTTP_INFO = lambda s: s
    return cmd


@pytest.mark.django_db
class TestGetPageFromSlug:
    def test_none_returns_none(self):
        assert _make_cmd().get_page_from_slug(None) is None

    def test_empty_string_returns_none(self):
        assert _make_cmd().get_page_from_slug("") is None

    def test_nonexistent_slug_returns_none(self):
        assert _make_cmd().get_page_from_slug("slug-that-does-not-exist-xyz") is None

    def test_matching_slug_returns_page(self, root_page):
        child = root_page.add_child(
            instance=Page(title="Search Slug Test", slug="search-slug-test", live=True)
        )
        result = _make_cmd().get_page_from_slug("search-slug-test")
        assert result is not None
        assert result.id == child.id


@pytest.mark.django_db
class TestUpdateSearchHandle:
    def test_completes_without_error_on_empty_db(self):
        cmd = _make_cmd()
        cmd.handle()
        assert "Finished updating all search promotions" in cmd.stdout.getvalue()

    def test_creates_promotion_for_page_matching_a_slug(self, root_page):
        from wagtail.contrib.search_promotions.models import SearchPromotion

        page = root_page.add_child(
            instance=Page(title="Petitioners", slug="petitioners", live=True)
        )
        _make_cmd().handle()

        assert SearchPromotion.objects.filter(page=page).exists()

    def test_skips_entries_with_no_matching_pages(self):
        from wagtail.contrib.search_promotions.models import SearchPromotion

        before = SearchPromotion.objects.count()
        _make_cmd().handle()
        assert SearchPromotion.objects.count() >= before
