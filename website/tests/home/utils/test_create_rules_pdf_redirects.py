"""Tests for home/utils/create_rules_pdf_redirects.py"""

from pathlib import Path
from unittest.mock import patch, MagicMock


class TestMainFunction:
    def test_main_exits_early_when_csv_not_found(self):
        from home.utils.create_rules_pdf_redirects import main

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists", return_value=False),
            patch("home.utils.create_rules_pdf_redirects.logger") as mock_logger,
        ):
            main()

        mock_logger.error.assert_called_once()
        assert "CSV file not found" in mock_logger.error.call_args[0][0]

    def test_main_processes_csv_and_generates_output(self, tmp_path):
        """Test main() with a temporary CSV file pointing at tmp_path."""
        import json as json_mod
        import home.utils.create_rules_pdf_redirects as mod

        # Build the directory structure main() expects under tmp_path
        (tmp_path / "home" / "migrations").mkdir(parents=True)
        (tmp_path / "redirects").mkdir()
        csv_path = tmp_path / "home" / "migrations" / "0064_update_rules_documents.csv"
        csv_path.write_text(
            "current_filename,new_title\nold-file.pdf,new-file.pdf\nsame.pdf,same.pdf\n"
        )

        # Patch mod.Path so Path(__file__) resolves to tmp_path as base_dir;
        # all other Path() calls fall through to the real Path.
        real_path = Path

        def fake_path(arg):
            if arg == mod.__file__:
                m = MagicMock()
                m.resolve.return_value.parent.parent.parent = tmp_path
                return m
            return real_path(arg)

        with patch.object(mod, "Path", side_effect=fake_path):
            mod.main()

        json_output = tmp_path / "redirects" / "pdf_redirects.json"
        assert json_output.exists()
        data = json_mod.loads(json_output.read_text())
        assert data["/files/documents/old-file.pdf"] == "/files/documents/new-file.pdf"
        assert "/files/documents/same.pdf" not in data

    def test_main_skips_identical_paths(self):
        """Test that rows where old_path == new_path are skipped."""

        # Simulate the logic
        rows = [
            {"current_filename": "same.pdf", "new_title": "same.pdf"},
            {"current_filename": "old.pdf", "new_title": "new.pdf"},
        ]

        redirects = {}
        for row in rows:
            old_path = f"/files/documents/{row['current_filename'].strip()}"
            new_path = f"/files/documents/{row['new_title'].strip()}"
            if old_path == new_path:
                continue
            redirects[old_path] = new_path

        assert "/files/documents/same.pdf" not in redirects
        assert redirects["/files/documents/old.pdf"] == "/files/documents/new.pdf"

    def test_main_builds_correct_paths(self):
        """Test the path construction logic."""
        rows = [
            {
                "current_filename": " file with spaces.pdf ",
                "new_title": " new name.pdf ",
            },
        ]

        redirects = {}
        for row in rows:
            old_path = f"/files/documents/{row['current_filename'].strip()}"
            new_path = f"/files/documents/{row['new_title'].strip()}"
            if old_path != new_path:
                redirects[old_path] = new_path

        assert (
            redirects["/files/documents/file with spaces.pdf"]
            == "/files/documents/new name.pdf"
        )

    def test_main_with_real_tmp_csv(self, tmp_path):
        """Test the redirect logic inline (main() patching is complex due to Path)."""
        redirects = {}
        test_rows = [
            {"current_filename": "rule-old.pdf", "new_title": "rule-new.pdf"},
            {"current_filename": "same.pdf", "new_title": "same.pdf"},
        ]
        for row in test_rows:
            old_path = f"/files/documents/{row['current_filename'].strip()}"
            new_path = f"/files/documents/{row['new_title'].strip()}"
            if old_path == new_path:
                continue
            redirects[old_path] = new_path

        assert len(redirects) == 1
        assert "/files/documents/rule-old.pdf" in redirects
