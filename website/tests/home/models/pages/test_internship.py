"""Tests for home/models/pages/internship.py"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch


class TestInternshipPageGetContext:
    def _make_internship_block(self, display_from, closing_date):
        block = MagicMock()
        block.block_type = "internship"
        block.value.get = lambda k, default=None: {
            "display_from": display_from,
            "closing_date": closing_date,
        }.get(k, default)
        return block

    def _make_page_with_blocks(self, blocks):
        from home.models.pages.internship import InternshipPrograms

        page = MagicMock(spec=InternshipPrograms)
        page.internship_programs = blocks
        return page

    def test_active_internship_included_in_context(self):
        from home.models.pages.internship import InternshipPrograms as InternshipPage

        today = date.today()
        block = self._make_internship_block(
            display_from=today - timedelta(days=1),
            closing_date=today + timedelta(days=10),
        )
        page = self._make_page_with_blocks([block])

        with patch(
            "home.models.pages.internship.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = InternshipPage.get_context(page, MagicMock())

        assert result["active_internships"] == [block]
        assert "no_opportunities_message" not in result

    def test_expired_internship_excluded(self):
        from home.models.pages.internship import InternshipPrograms as InternshipPage

        today = date.today()
        block = self._make_internship_block(
            display_from=today - timedelta(days=5),
            closing_date=today - timedelta(days=1),  # expired
        )
        page = self._make_page_with_blocks([block])

        with patch(
            "home.models.pages.internship.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = InternshipPage.get_context(page, MagicMock())

        assert result["active_internships"] == []
        assert "no_opportunities_message" in result

    def test_future_internship_not_yet_displayed(self):
        from home.models.pages.internship import InternshipPrograms as InternshipPage

        today = date.today()
        block = self._make_internship_block(
            display_from=today + timedelta(days=5),  # future
            closing_date=today + timedelta(days=20),
        )
        page = self._make_page_with_blocks([block])

        with patch(
            "home.models.pages.internship.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = InternshipPage.get_context(page, MagicMock())

        assert result["active_internships"] == []
        assert "no_opportunities_message" in result

    def test_h2_and_paragraph_blocks_always_included(self):
        from home.models.pages.internship import InternshipPrograms as InternshipPage

        today = date.today()
        h2_block = MagicMock()
        h2_block.block_type = "h2"
        paragraph_block = MagicMock()
        paragraph_block.block_type = "paragraph"

        active_block = self._make_internship_block(
            display_from=today - timedelta(days=1),
            closing_date=today + timedelta(days=10),
        )
        page = self._make_page_with_blocks([h2_block, paragraph_block, active_block])

        with patch(
            "home.models.pages.internship.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = InternshipPage.get_context(page, MagicMock())

        assert h2_block in result["active_internships"]
        assert paragraph_block in result["active_internships"]
        assert active_block in result["active_internships"]
