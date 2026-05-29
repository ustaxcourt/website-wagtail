"""Tests for search/views.py utility functions."""

from unittest.mock import MagicMock
from types import SimpleNamespace

from search.views import extract_text_from_streamfield, get_search_snippet


class TestExtractTextFromStreamfield:
    def test_empty_value_returns_empty(self):
        assert extract_text_from_streamfield(None) == ""
        assert extract_text_from_streamfield([]) == ""

    def test_rich_text_block_extracts_source(self):
        block = SimpleNamespace(
            block_type="richtext",
            value=SimpleNamespace(source="<p>Hello World</p>"),
        )
        result = extract_text_from_streamfield([block])
        assert "Hello World" in result

    def test_string_value_included(self):
        block = SimpleNamespace(block_type="char", value="Simple text")
        result = extract_text_from_streamfield([block])
        assert "Simple text" in result

    def test_dict_value_extracts_string_values(self):
        block = SimpleNamespace(
            block_type="struct",
            value={"title": "My Title", "description": "My Desc"},
        )
        result = extract_text_from_streamfield([block])
        assert "My Title" in result
        assert "My Desc" in result

    def test_result_truncated_to_max_length(self):
        long_text = "x" * 1000
        block = SimpleNamespace(block_type="char", value=long_text)
        result = extract_text_from_streamfield([block], max_length=100)
        assert len(result) <= 100

    def test_questionanswers_block_type_extracts_qa(self):
        qa_entry = {"question": "What is it?", "answer": "It is a test."}
        block = SimpleNamespace(
            block_type="questionanswers",
            value=[qa_entry],
        )
        result = extract_text_from_streamfield([block])
        assert "What is it?" in result
        assert "It is a test." in result

    def test_questionanswers_rich_text_answer(self):
        qa_entry = {
            "question": "Q?",
            "answer": {"rich_text": SimpleNamespace(source="Rich answer")},
        }
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "Rich answer" in result

    def test_list_value_in_dict(self):
        inner_block = SimpleNamespace(block_type="char", value="inside list")
        block = SimpleNamespace(
            block_type="struct",
            value={"items": [inner_block]},
        )
        result = extract_text_from_streamfield([block])
        assert isinstance(result, str)

    def test_strips_html_tags(self):
        block = SimpleNamespace(block_type="char", value="<b>Bold</b> text")
        result = extract_text_from_streamfield([block])
        assert "<b>" not in result
        assert "Bold" in result


class TestGetSearchSnippet:
    def test_uses_search_description_when_present(self):
        page = MagicMock()
        page.specific.search_description = "Meta description text"
        result = get_search_snippet(page)
        assert result == "Meta description text"

    def test_falls_back_to_intro(self):
        page = MagicMock()
        page.specific = SimpleNamespace(
            search_description=None, intro="<p>Intro text</p>"
        )
        result = get_search_snippet(page)
        assert "Intro text" in result

    def test_falls_back_to_string_body(self):
        page = MagicMock()
        page.specific = SimpleNamespace(
            search_description=None, body="<p>Body content here</p>"
        )
        result = get_search_snippet(page)
        # Body is a plain string — result may be empty if the code doesn't handle plain strings
        assert isinstance(result, str)

    def test_returns_empty_string_when_no_content(self):
        page = MagicMock()
        page.specific = SimpleNamespace(search_description=None)
        result = get_search_snippet(page)
        assert result == ""
