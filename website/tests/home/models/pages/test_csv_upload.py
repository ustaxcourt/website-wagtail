"""Tests for home/models/pages/csv_upload.py"""

from unittest.mock import patch, MagicMock


class TestCSVUploadPageGetContext:
    def _make_page(self):
        from home.models.pages.csv_upload import CSVUploadPage

        page = CSVUploadPage.__new__(CSVUploadPage)
        return page

    def test_no_csv_file_sets_csv_data_none(self):
        page = self._make_page()
        page.csv_file = None

        request = MagicMock()
        with patch(
            "home.models.pages.enhanced_standard.EnhancedStandardPage.get_context",
            return_value={},
        ):
            context = page.get_context(request)

        assert context["csv_data"] is None

    def test_csv_file_with_data_sets_csv_data(self):
        page = self._make_page()
        page.csv_file = MagicMock()  # truthy

        request = MagicMock()
        mock_csv_data = {"headers": ["col1", "col2"], "rows": [["a", "b"]]}

        with patch(
            "home.models.pages.enhanced_standard.EnhancedStandardPage.get_context",
            return_value={},
        ):
            with patch.object(page, "get_csv_data", return_value=mock_csv_data):
                context = page.get_context(request)

        assert context["csv_data"] == mock_csv_data

    def test_csv_file_with_empty_data_sets_csv_data_none(self):
        page = self._make_page()
        page.csv_file = MagicMock()  # truthy

        request = MagicMock()
        mock_csv_data = {"headers": [], "rows": []}

        with patch(
            "home.models.pages.enhanced_standard.EnhancedStandardPage.get_context",
            return_value={},
        ):
            with patch.object(page, "get_csv_data", return_value=mock_csv_data):
                context = page.get_context(request)

        assert context["csv_data"] is None

    def test_csv_file_with_headers_but_no_rows_sets_none(self):
        page = self._make_page()
        page.csv_file = MagicMock()

        request = MagicMock()
        mock_csv_data = {"headers": ["col1"], "rows": []}

        with patch(
            "home.models.pages.enhanced_standard.EnhancedStandardPage.get_context",
            return_value={},
        ):
            with patch.object(page, "get_csv_data", return_value=mock_csv_data):
                context = page.get_context(request)

        assert context["csv_data"] is None


class TestCSVUploadPageGetCsvData:
    def _make_page(self):
        from home.models.pages.csv_upload import CSVUploadPage

        page = CSVUploadPage.__new__(CSVUploadPage)
        return page

    def test_parses_csv_string_content(self):
        page = self._make_page()
        csv_content = "header1,header2\nvalue1,value2\n"
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.read.return_value = csv_content
        page.csv_file = MagicMock()
        page.csv_file.open.return_value = mock_file

        result = page.get_csv_data()

        assert result["headers"] == ["header1", "header2"]
        assert result["rows"] == [["value1", "value2"]]

    def test_parses_csv_bytes_content(self):
        page = self._make_page()
        csv_content = b"colA,colB\nrow1a,row1b\n"
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.read.return_value = csv_content
        page.csv_file = MagicMock()
        page.csv_file.open.return_value = mock_file

        result = page.get_csv_data()

        assert result["headers"] == ["colA", "colB"]
        assert result["rows"] == [["row1a", "row1b"]]

    def test_handles_empty_csv(self):
        page = self._make_page()
        csv_content = ""
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.read.return_value = csv_content
        page.csv_file = MagicMock()
        page.csv_file.open.return_value = mock_file

        result = page.get_csv_data()

        assert result["headers"] == []
        assert result["rows"] == []
