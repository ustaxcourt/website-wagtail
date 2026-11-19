"""Tests for StandardPage in home/models/pages/standard.py"""

from types import SimpleNamespace

import pytest
from wagtail.models import Locale, Page

from home.models.pages.standard import StandardPage


class TestSearchSnippetBranches:
    """search_snippet picks a strategy based on the shape of `body`/`intro`."""

    def _page(self, **attrs):
        page = StandardPage.__new__(StandardPage)
        page.__dict__.update(attrs)
        return page

    def test_html_body_is_stripped(self):
        assert (
            self._page(body="<p>Hello <b>there</b></p>").search_snippet == "Hello there"
        )

    def test_html_body_truncated_to_300(self):
        assert len(self._page(body="x" * 500).search_snippet) == 300

    def test_streamfield_like_body_uses_extractor(self):
        block = SimpleNamespace(value="Streamed <i>text</i>")

        class FakeStream(list):
            blocks = True

        page = self._page(body=FakeStream([block]))
        assert page.search_snippet == "Streamed text"

    def test_stream_data_attribute_also_uses_extractor(self):
        class FakeStream(list):
            stream_data = []

        page = self._page(body=FakeStream([SimpleNamespace(value="From stream")]))
        assert page.search_snippet == "From stream"

    def test_falls_back_to_intro_when_body_not_string(self):
        page = self._page(body=None, intro="<p>Intro text</p>")
        assert page.search_snippet == "Intro text"

    def test_intro_truncated_to_300(self):
        page = self._page(body=None, intro="y" * 400)
        assert len(page.search_snippet) == 300

    def test_empty_string_when_no_body_or_intro(self):
        # An unset body on a bare instance has no usable attributes.
        page = self._page(body=None)
        assert page.search_snippet == ""


@pytest.mark.django_db
class TestStandardPageTree:
    def _create(self, **kwargs):
        Locale.objects.get_or_create(language_code="en")
        root = Page.get_first_root_node() or Page.add_root(title="Root", slug="root")
        page = StandardPage(title="Standard", slug="standard", **kwargs)
        root.add_child(instance=page)
        return page

    def test_page_saves_in_tree_and_snippet_reads_body(self):
        page = self._create(body="<p>Tree body</p>")
        page.refresh_from_db()
        assert page.search_snippet == "Tree body"

    def test_blank_body_gives_empty_snippet(self):
        page = self._create(body="")
        assert page.search_snippet == ""

    def test_search_fields_include_body(self):
        names = [getattr(f, "field_name", None) for f in StandardPage.search_fields]
        assert "body" in names

    def test_moderation_fields_available(self):
        page = self._create()
        assert page.review_by is None
        assert page.is_review_overdue is False
        assert page.days_until_review is None
