"""Tests for home/management/commands/update_search.py"""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from home.management.commands.update_search import Command


class TestGetPageFromSlug:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        cmd.style = MagicMock()
        cmd.style.WARNING = lambda s: s
        cmd.style.ERROR = lambda s: s
        return cmd


@pytest.mark.django_db
class TestUpdateSearchHandle:
    def test_handle_with_no_matching_pages_does_not_crash(self):
        cmd = Command()
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        # With empty DB, no pages will be found, so handle should complete without error
        with patch.object(cmd, "get_page_from_slug", return_value=None):
            cmd.handle()
        # Should have completed


class TestGetPageFromSlugStatic:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.WARNING = lambda s: s
        return cmd

    def test_none_text_returns_none(self):
        cmd = self._make_cmd()
        assert cmd.get_page_from_slug(None) is None
        assert cmd.get_page_from_slug("") is None

    @pytest.mark.django_db
    def test_nonexistent_slug_returns_none(self):
        cmd = self._make_cmd()
        result = cmd.get_page_from_slug("this-slug-does-not-exist-xyz")
        assert result is None
