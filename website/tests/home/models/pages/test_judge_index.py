"""Tests for home/models/pages/judge_index.py"""

import pytest
from unittest.mock import MagicMock, patch
from django.http import Http404


class TestJudgeIndexGetContext:
    def test_get_context_returns_judge_groups_and_jcdp_url(self):
        """`get_context` populates the rendering context with judge_groups
        (the list built by `_build_judge_groups`) and a judicial_conduct_url.

        Previously this test asserted a "roles" key that the current
        implementation does not produce. Updated to match the JudgeIndex
        get_context implementation in WAG-1246.
        """
        from home.models.pages.judge_index import JudgeIndex

        page = MagicMock(spec=JudgeIndex)
        mock_groups = [MagicMock(), MagicMock()]
        page._build_judge_groups.return_value = mock_groups

        mock_jcdp = MagicMock(url="/judicial-conduct-and-disability-procedures/")

        with (
            patch(
                "home.models.pages.judge_index.Page.get_context",
                return_value={},
            ),
            patch(
                "home.models.pages.judge_index.Page.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=mock_jcdp)),
            ),
        ):
            result = JudgeIndex.get_context(page, MagicMock())

        assert result["judge_groups"] == mock_groups
        assert (
            result["judicial_conduct_url"]
            == "/judicial-conduct-and-disability-procedures/"
        )

    def test_get_context_jcdp_url_falls_back_to_hash_when_page_missing(self):
        """If the JCDP page hasn't been created yet, the helper returns '#'."""
        from home.models.pages.judge_index import JudgeIndex

        page = MagicMock(spec=JudgeIndex)
        page._build_judge_groups.return_value = []

        with (
            patch(
                "home.models.pages.judge_index.Page.get_context",
                return_value={},
            ),
            patch(
                "home.models.pages.judge_index.Page.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=None)),
            ),
        ):
            result = JudgeIndex.get_context(page, MagicMock())

        assert result["judicial_conduct_url"] == "#"


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
