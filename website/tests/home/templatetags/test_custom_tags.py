"""Tests for home/templatetags/custom_tags.py"""

from unittest.mock import MagicMock
from home.templatetags.custom_tags import phone_link, clean_filename


class TestPhoneLink:
    def test_formats_standard_phone(self):
        result = phone_link("(202) 555-1234")
        assert "tel:2025551234" in result
        assert "(202) 555-1234" in result

    def test_strips_parens_dashes_spaces(self):
        result = phone_link("(800) 123-4567")
        assert "tel:8001234567" in result

    def test_phone_with_no_formatting(self):
        result = phone_link("5551234567")
        assert "tel:5551234567" in result

    def test_none_returns_none(self):
        assert phone_link(None) is None

    def test_empty_string_returns_empty(self):
        result = phone_link("")
        assert result == ""

    def test_result_is_anchor_tag(self):
        result = phone_link("555-1234")
        assert result.startswith("<a href=")
        assert "</a>" in result


class TestCleanFilename:
    def test_removes_extension(self):
        assert clean_filename("document.pdf") == "document"

    def test_replaces_dashes_with_spaces(self):
        assert clean_filename("my-document") == "my document"

    def test_replaces_underscores_with_spaces(self):
        assert clean_filename("my_document") == "my document"

    def test_removes_extension_and_replaces_separators(self):
        assert clean_filename("my-file_name.pdf") == "my file name"

    def test_no_extension_no_separators(self):
        assert clean_filename("document") == "document"

    def test_multiple_dots_strips_last_extension(self):
        # clean_filename strips only the last extension (rsplit behavior)
        result = clean_filename("archive.tar.gz")
        assert result == "archive.tar"


class TestGetType:
    def test_returns_type_name_for_string(self):
        from home.templatetags.custom_tags import get_type as gt

        assert gt("hello") == "str"

    def test_returns_type_name_for_int(self):
        from home.templatetags.custom_tags import get_type as gt

        assert gt(42) == "int"

    def test_returns_type_name_for_list(self):
        from home.templatetags.custom_tags import get_type as gt

        assert gt([]) == "list"

    def test_returns_type_name_for_none(self):
        from home.templatetags.custom_tags import get_type as gt

        assert gt(None) == "NoneType"


class TestIncludeSvg:
    def test_non_svg_document_returns_empty(self):
        from home.templatetags.custom_tags import include_svg

        doc = MagicMock()
        doc.file.name = "document.pdf"
        result = include_svg(doc)
        assert result == ""

    def test_none_document_returns_empty(self):
        from home.templatetags.custom_tags import include_svg

        result = include_svg(None)
        assert result == ""

    def test_svg_document_returns_content(self):
        from home.templatetags.custom_tags import include_svg

        doc = MagicMock()
        doc.file.name = "icon.svg"
        doc.file.read.return_value = b"<svg>test</svg>"
        result = include_svg(doc)
        assert "<svg>" in str(result)

    def test_svg_document_io_error_returns_empty(self):
        from home.templatetags.custom_tags import include_svg

        doc = MagicMock()
        doc.file.name = "icon.svg"
        doc.file.open.side_effect = IOError("file not found")
        result = include_svg(doc)
        assert result == ""
