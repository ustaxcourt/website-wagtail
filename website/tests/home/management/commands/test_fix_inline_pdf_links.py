"""Tests for fix_inline_pdf_links management command helper methods."""

from io import StringIO
from unittest.mock import MagicMock, patch
from home.management.commands.fix_inline_pdf_links import Command


class TestProcessHtmlContent:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.page_replacements = []
        cmd.dry_run = False
        cmd.verbose = False
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        cmd.style.WARNING = lambda s: s
        return cmd

    def test_returns_unchanged_when_no_pdf_link(self):
        cmd = self._make_cmd()
        html = "<p>No links here</p>"
        result, count = cmd.process_html_content(html)
        assert result == html
        assert count == 0

    def test_returns_unchanged_when_empty(self):
        cmd = self._make_cmd()
        result, count = cmd.process_html_content("")
        assert result == ""
        assert count == 0

    def test_replaces_pdf_link_when_document_found(self):
        cmd = self._make_cmd()
        mock_doc = MagicMock()
        mock_doc.id = 42
        mock_doc.title = "Test Document"
        cmd.find_document_by_filename = MagicMock(return_value=mock_doc)
        html = '<p><a href="/docs/test.pdf">Download</a></p>'
        result, count = cmd.process_html_content(html)
        assert count == 1
        assert 'linktype="document"' in result
        assert 'id="42"' in result

    def test_does_not_replace_when_document_not_found(self):
        cmd = self._make_cmd()
        cmd.find_document_by_filename = MagicMock(return_value=None)
        html = '<p><a href="/docs/missing.pdf">Download</a></p>'
        result, count = cmd.process_html_content(html)
        assert count == 0

    def test_dry_run_still_replaces_link_in_html(self):
        cmd = self._make_cmd()
        cmd.dry_run = True
        mock_doc = MagicMock()
        mock_doc.id = 5
        mock_doc.title = "Doc"
        cmd.find_document_by_filename = MagicMock(return_value=mock_doc)
        html = '<p><a href="/docs/test.pdf">Download</a></p>'
        result, count = cmd.process_html_content(html)
        assert count == 1
        # In dry-run, HTML is still updated (dry-run prevents DB save, not HTML transform)
        assert 'linktype="document"' in result


class TestProcessStructBlock:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.page_replacements = []
        cmd.dry_run = False
        cmd.verbose = False
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        return cmd

    def test_string_value_no_pdf_link(self):
        cmd = self._make_cmd()
        struct = {"title": "Hello world"}
        result = cmd.process_struct_block(struct)
        assert result == 0


class TestProcessListBlock:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.page_replacements = []
        cmd.dry_run = False
        cmd.verbose = False
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        return cmd

    def test_empty_list_returns_zero(self):
        cmd = self._make_cmd()
        result = cmd.process_list_block([])
        assert result == 0

    def test_string_item_no_pdf(self):
        cmd = self._make_cmd()
        result = cmd.process_list_block(["plain text"])
        assert result == 0

    def test_dict_item_processed(self):
        cmd = self._make_cmd()
        # Dict items are passed to process_struct_block
        result = cmd.process_list_block([{"title": "hello"}])
        assert result == 0

    def test_list_item_nested(self):
        cmd = self._make_cmd()
        # Nested lists
        result = cmd.process_list_block([["inner text"]])
        assert result == 0

    def test_richtext_item_replaced_when_found(self):
        from wagtail.rich_text import RichText

        cmd = self._make_cmd()
        mock_doc = MagicMock()
        mock_doc.id = 10
        mock_doc.title = "Test"
        cmd.find_document_by_filename = MagicMock(return_value=mock_doc)
        rich_text = MagicMock(spec=RichText)
        rich_text.source = '<a href="/docs/test.pdf">PDF</a>'
        rich_text.__class__ = RichText
        result = cmd.process_list_block([rich_text])
        assert result == 1

    def test_struct_item_processed(self):
        cmd = self._make_cmd()
        struct = MagicMock()
        struct.items = lambda: [("title", "hello")]
        result = cmd.process_list_block([struct])
        assert result == 0


class TestProcessStructBlockExtra:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.page_replacements = []
        cmd.dry_run = False
        cmd.verbose = False
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        return cmd

    def test_nested_dict_value_processed(self):
        cmd = self._make_cmd()
        struct = {"outer": {"inner": "text"}}
        result = cmd.process_struct_block(struct)
        assert result == 0

    def test_nested_list_value_processed(self):
        cmd = self._make_cmd()
        struct = {"items": ["text1", "text2"]}
        result = cmd.process_struct_block(struct)
        assert result == 0

    def test_richtext_value_replaced(self):
        from wagtail.rich_text import RichText

        cmd = self._make_cmd()
        mock_doc = MagicMock()
        mock_doc.id = 20
        mock_doc.title = "Doc"
        cmd.find_document_by_filename = MagicMock(return_value=mock_doc)
        rich_text = RichText('<a href="/docs/test.pdf">PDF</a>')
        struct = {"content": rich_text}
        result = cmd.process_struct_block(struct)
        assert result == 1


class TestHandleCommand:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.processed_pages = 0
        cmd.total_replacements = 0
        cmd.page_replacements = []
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        cmd.style.WARNING = lambda s: s
        cmd.style.ERROR = lambda s: s
        return cmd

    def test_handle_dry_run_flag_set(self):
        cmd = self._make_cmd()
        with patch.object(cmd, "process_all_pages"):
            cmd.handle(dry_run=True, verbose=False, page_id=None)
            assert cmd.dry_run is True

    def test_handle_processes_all_pages_by_default(self):
        cmd = self._make_cmd()
        with patch.object(cmd, "process_all_pages") as mock_all:
            cmd.handle(dry_run=False, verbose=False, page_id=None)
            mock_all.assert_called_once()

    def test_handle_processes_specific_page_by_id(self):
        cmd = self._make_cmd()
        mock_page = MagicMock()
        mock_page.specific = mock_page
        with patch(
            "home.management.commands.fix_inline_pdf_links.Page"
        ) as mock_page_cls:
            mock_page_cls.objects.get.return_value = mock_page
            with patch.object(cmd, "process_single_page") as mock_single:
                cmd.handle(dry_run=False, verbose=False, page_id=42)
                mock_single.assert_called_once()

    def test_handle_handles_page_not_found(self):
        cmd = self._make_cmd()
        from wagtail.models import Page

        with patch.object(Page.objects, "get", side_effect=Page.DoesNotExist):
            cmd.handle(dry_run=False, verbose=False, page_id=999)
            # Should write error and return without crashing


class TestFindDocumentByFilename:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.page_replacements = []
        cmd.dry_run = False
        cmd.verbose = False
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        return cmd

    def test_returns_document_on_exact_match(self):
        cmd = self._make_cmd()
        mock_doc = MagicMock()
        cmd.Document.objects.filter.return_value.first.return_value = mock_doc
        result = cmd.find_document_by_filename("test.pdf")
        assert result is mock_doc

    def test_falls_back_to_base_name_when_no_exact_match(self):
        cmd = self._make_cmd()
        mock_doc = MagicMock()
        # First call returns None, second returns mock_doc
        cmd.Document.objects.filter.return_value.first.side_effect = [None, mock_doc]
        result = cmd.find_document_by_filename("test.pdf")
        assert result is mock_doc

    def test_returns_none_on_exception(self):
        cmd = self._make_cmd()
        cmd.Document.objects.filter.side_effect = Exception("DB error")
        result = cmd.find_document_by_filename("test.pdf")
        assert result is None


class TestProcessSinglePage:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.Document = MagicMock()
        cmd.processed_pages = 0
        cmd.total_replacements = 0
        cmd.page_replacements = []
        cmd.dry_run = False
        cmd.verbose = False
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda s: s
        cmd.style.WARNING = lambda s: s
        return cmd

    def test_process_page_without_body_no_crash(self):
        cmd = self._make_cmd()
        page = MagicMock()
        page.title = "Test Page"
        page.id = 1
        page.slug = "test"
        del page.body  # page has no body
        page._meta.get_fields.return_value = []
        cmd.process_single_page(page)
        # No crash, no replacements
        assert cmd.processed_pages == 0

    def test_process_page_with_body_calls_process_streamfield(self):
        cmd = self._make_cmd()
        page = MagicMock()
        page.title = "Test"
        page.id = 1
        page.slug = "test"
        page.body = [MagicMock()]
        page._meta.get_fields.return_value = []
        with patch.object(cmd, "process_streamfield", return_value=(page.body, 0)):
            cmd.process_single_page(page)

    def test_process_page_saves_when_replacements_made(self):
        cmd = self._make_cmd()
        page = MagicMock()
        page.title = "Test"
        page.id = 1
        page.slug = "test"
        page.body = [MagicMock()]
        page._meta.get_fields.return_value = []
        cmd.page_replacements = [("file.pdf", "Doc", 1)]
        with patch.object(cmd, "process_streamfield", return_value=(page.body, 1)):
            with patch("home.management.commands.fix_inline_pdf_links.transaction"):
                cmd.process_single_page(page)
                page.save.assert_called_once()
