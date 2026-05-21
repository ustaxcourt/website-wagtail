"""Tests for home/utils/document_collection_and_tag_assignment.py"""

from unittest.mock import patch
from home.utils.document_collection_and_tag_assignment import (
    get_tags_for_document,
    get_collection_for_document,
)


class TestGetTagsForDocument:
    def test_returns_empty_list_for_unknown_document(self):
        with patch(
            "home.utils.document_collection_and_tag_assignment.DOCUMENT_TAGS_MAP", {}
        ):
            result = get_tags_for_document("unknown_doc.pdf")
        assert result == []

    def test_returns_tags_for_known_document(self):
        mock_map = {"doc.pdf": {"tags": ["Tax", "Rules"]}}
        with (
            patch(
                "home.utils.document_collection_and_tag_assignment.DOCUMENT_TAGS_MAP",
                mock_map,
            ),
            patch(
                "home.utils.document_collection_and_tag_assignment.ROLE_TAGS_TAG_MAP",
                {},
            ),
        ):
            result = get_tags_for_document("doc.pdf")
        assert "Tax" in result
        assert "Rules" in result

    def test_adds_role_tag_when_overlap(self):
        mock_map = {"doc.pdf": {"tags": ["Tax"]}}
        mock_role_map = {"TaxPro": ["Tax", "Other"]}
        with (
            patch(
                "home.utils.document_collection_and_tag_assignment.DOCUMENT_TAGS_MAP",
                mock_map,
            ),
            patch(
                "home.utils.document_collection_and_tag_assignment.ROLE_TAGS_TAG_MAP",
                mock_role_map,
            ),
        ):
            result = get_tags_for_document("doc.pdf")
        assert "TaxPro" in result

    def test_does_not_add_role_tag_when_no_overlap(self):
        mock_map = {"doc.pdf": {"tags": ["Unrelated"]}}
        mock_role_map = {"TaxPro": ["Tax", "Other"]}
        with (
            patch(
                "home.utils.document_collection_and_tag_assignment.DOCUMENT_TAGS_MAP",
                mock_map,
            ),
            patch(
                "home.utils.document_collection_and_tag_assignment.ROLE_TAGS_TAG_MAP",
                mock_role_map,
            ),
        ):
            result = get_tags_for_document("doc.pdf")
        assert "TaxPro" not in result


class TestGetCollectionForDocument:
    def test_returns_first_matching_collection(self):
        with patch(
            "home.utils.document_collection_and_tag_assignment.COLLECTION_SORTING_ORDER",
            ["Tax", "Rules", "Other"],
        ):
            result = get_collection_for_document("doc.pdf", ["Rules", "Tax"])
        assert result == "Tax"

    def test_returns_none_when_no_match(self, capsys):
        with patch(
            "home.utils.document_collection_and_tag_assignment.COLLECTION_SORTING_ORDER",
            ["Tax", "Rules"],
        ):
            result = get_collection_for_document("doc.pdf", ["Unrelated"])
        assert result is None
        captured = capsys.readouterr()
        assert "No collection exist" in captured.out

    def test_returns_none_with_empty_tags(self):
        with patch(
            "home.utils.document_collection_and_tag_assignment.COLLECTION_SORTING_ORDER",
            ["Tax"],
        ):
            result = get_collection_for_document("doc.pdf", [])
        assert result is None
