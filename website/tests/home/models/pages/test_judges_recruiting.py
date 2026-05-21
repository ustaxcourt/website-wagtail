"""Tests for home/models/pages/judges_recruiting.py"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch


class TestJudgesRecruitingGetContext:
    def _make_judge_value(self, display_from=None, display_to=None):
        return {
            "display_from": display_from,
            "display_to": display_to,
            "judge_name": "Judge Smith",
        }

    def _make_judge_block(self, judges):
        block = MagicMock()
        block.block_type = "judge"
        block.value = judges
        return block

    def test_active_judge_included(self):
        from home.models.pages.judges_recruiting import JudgesRecruiting

        page = MagicMock(spec=JudgesRecruiting)
        today = date.today()
        judge = self._make_judge_value(
            display_from=today - timedelta(days=1),
            display_to=today + timedelta(days=10),
        )
        block = self._make_judge_block([judge])
        page.judges_recruiting = [block]

        with patch(
            "home.models.pages.judges_recruiting.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = JudgesRecruiting.get_context(page, MagicMock())

        assert judge in result["judges_recruiting"]

    def test_expired_judge_excluded(self):
        from home.models.pages.judges_recruiting import JudgesRecruiting

        page = MagicMock(spec=JudgesRecruiting)
        today = date.today()
        judge = self._make_judge_value(
            display_from=today - timedelta(days=5),
            display_to=today - timedelta(days=1),  # expired
        )
        block = self._make_judge_block([judge])
        page.judges_recruiting = [block]

        with patch(
            "home.models.pages.judges_recruiting.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = JudgesRecruiting.get_context(page, MagicMock())

        assert judge not in result["judges_recruiting"]

    def test_judge_with_no_dates_included(self):
        from home.models.pages.judges_recruiting import JudgesRecruiting

        page = MagicMock(spec=JudgesRecruiting)
        judge = self._make_judge_value()  # No dates
        block = self._make_judge_block([judge])
        page.judges_recruiting = [block]

        with patch(
            "home.models.pages.judges_recruiting.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = JudgesRecruiting.get_context(page, MagicMock())

        assert judge in result["judges_recruiting"]

    def test_message_block_sets_context(self):
        from home.models.pages.judges_recruiting import JudgesRecruiting

        page = MagicMock(spec=JudgesRecruiting)
        msg_block = MagicMock()
        msg_block.block_type = "message"
        msg_block.value = "No judges recruiting currently."
        page.judges_recruiting = [msg_block]

        with patch(
            "home.models.pages.judges_recruiting.EnhancedStandardPage.get_context",
            return_value={},
        ):
            result = JudgesRecruiting.get_context(page, MagicMock())

        assert result["message"] == "No judges recruiting currently."
