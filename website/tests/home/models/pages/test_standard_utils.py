"""Tests for home/models/pages/standard.py utility functions."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from home.models.pages.standard import extract_text_from_streamfield


class TestExtractTextFromStreamfieldStandard:
    def test_empty_returns_empty_string(self):
        assert extract_text_from_streamfield(None) == ""
        assert extract_text_from_streamfield([]) == ""

    def test_string_value(self):
        block = SimpleNamespace(value="Hello World")
        result = extract_text_from_streamfield([block])
        assert "Hello World" in result

    def test_rich_text_source(self):
        block = SimpleNamespace(value=SimpleNamespace(source="<p>Rich text</p>"))
        result = extract_text_from_streamfield([block])
        assert "Rich text" in result

    def test_dict_value(self):
        block = SimpleNamespace(value={"title": "Dict Title", "desc": "Dict Desc"})
        result = extract_text_from_streamfield([block])
        assert "Dict Title" in result
        assert "Dict Desc" in result

    def test_strips_html(self):
        block = SimpleNamespace(value="<b>Bold</b> text")
        result = extract_text_from_streamfield([block])
        assert "<b>" not in result
        assert "Bold" in result

    def test_truncates_to_max_length(self):
        block = SimpleNamespace(value="a" * 1000)
        result = extract_text_from_streamfield([block], max_length=50)
        assert len(result) <= 50

    def test_list_value(self):
        inner_block = SimpleNamespace(value="Inner text")
        block = SimpleNamespace(value=[inner_block])
        result = extract_text_from_streamfield([block])
        assert isinstance(result, str)

    def test_dict_value_with_nested_stream(self):
        inner = MagicMock()
        inner.stream_data = []
        block = SimpleNamespace(value={"nested": inner})
        result = extract_text_from_streamfield([block])
        assert isinstance(result, str)

    def test_dict_value_with_nested_list(self):
        inner_block = SimpleNamespace(value="list text")
        block = SimpleNamespace(value={"items": [inner_block]})
        result = extract_text_from_streamfield([block])
        assert isinstance(result, str)

    def test_nested_streamblock_value(self):
        inner_block = SimpleNamespace(value="nested")
        nested = MagicMock()
        nested.stream_data = []
        nested.__iter__ = lambda s: iter([inner_block])
        block = SimpleNamespace(value=nested)
        result = extract_text_from_streamfield([block])
        assert isinstance(result, str)


class TestStandardPageSearchSnippet:
    def test_search_snippet_strips_html_from_body(self):
        from home.models.pages.standard import StandardPage

        page = StandardPage.__new__(StandardPage)
        page.__dict__["body"] = "<p>Hello world</p>"
        result = StandardPage.search_snippet.fget(page)
        assert "Hello world" in result
        assert "<p>" not in result

    def test_search_snippet_returns_empty_when_body_is_empty(self):
        from home.models.pages.standard import StandardPage

        page = StandardPage.__new__(StandardPage)
        page.__dict__["body"] = ""
        result = StandardPage.search_snippet.fget(page)
        assert result == ""

    def test_search_snippet_truncates_to_300_chars(self):
        from home.models.pages.standard import StandardPage

        page = StandardPage.__new__(StandardPage)
        page.__dict__["body"] = "x" * 500
        result = StandardPage.search_snippet.fget(page)
        assert len(result) <= 300
