"""Tests for home/models/pages/judge_index.py"""

import pytest
from unittest.mock import MagicMock, patch
from django.http import Http404


class TestJudgeIndexGetContext:
    def test_get_context_returns_roles(self):
        from home.models.pages.judge_index import JudgeIndex

        page = MagicMock(spec=JudgeIndex)
        mock_roles = [MagicMock(), MagicMock()]

        with (
            patch(
                "home.models.pages.judge_index.Page.get_context",
                return_value={},
            ),
            patch(
                "home.models.pages.judge_index.JudgeRole.objects.filter",
                return_value=mock_roles,
            ),
        ):
            result = JudgeIndex.get_context(page, MagicMock())

        assert result["roles"] == mock_roles


class TestJudgeIndexJudgeDetail:
    def test_judge_detail_renders_with_matching_last_name(self):
        from home.models.pages.judge_index import JudgeIndex

        page = MagicMock(spec=JudgeIndex)
        page.get_context.return_value = {}

        mock_judge = MagicMock()
        mock_judge.last_name = "Smith"

        with (
            patch(
                "home.models.pages.judge_index.JudgeProfile.objects.get",
                return_value=mock_judge,
            ),
            patch(
                "home.models.pages.judge_index.render",
                return_value=MagicMock(),
            ) as mock_render,
        ):
            JudgeIndex.judge_detail(page, MagicMock(), id="1", last_name="smith")
            mock_render.assert_called_once()

    def test_judge_detail_raises_404_when_last_name_mismatch(self):
        from home.models.pages.judge_index import JudgeIndex

        page = MagicMock(spec=JudgeIndex)
        page.get_context.return_value = {}

        mock_judge = MagicMock()
        mock_judge.last_name = "Smith"

        with (
            patch(
                "home.models.pages.judge_index.JudgeProfile.objects.get",
                return_value=mock_judge,
            ),
        ):
            with pytest.raises(Http404):
                JudgeIndex.judge_detail(page, MagicMock(), id="1", last_name="jones")

    def test_judge_detail_raises_404_when_not_found(self):
        from home.models.pages.judge_index import JudgeIndex

        page = MagicMock(spec=JudgeIndex)

        from home.models.snippets.judges import JudgeProfile

        with patch(
            "home.models.pages.judge_index.JudgeProfile.objects.get",
            side_effect=JudgeProfile.DoesNotExist,
        ):
            with pytest.raises(Http404):
                JudgeIndex.judge_detail(page, MagicMock(), id="999", last_name="nobody")
