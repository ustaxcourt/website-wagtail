"""Tests for home/models/pages/home_page.py"""

import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch
from django import forms
from django.utils import timezone


class TestHomePageAdminFormCleanIntroText:
    def test_raises_validation_error_when_empty(self):
        from home.models.pages.home_page import HomePageAdminForm

        form = HomePageAdminForm.__new__(HomePageAdminForm)
        form.cleaned_data = {"intro_text": ""}
        with pytest.raises(forms.ValidationError):
            form.clean_intro_text()

    def test_raises_validation_error_when_whitespace(self):
        from home.models.pages.home_page import HomePageAdminForm

        form = HomePageAdminForm.__new__(HomePageAdminForm)
        form.cleaned_data = {"intro_text": "   "}
        with pytest.raises(forms.ValidationError):
            form.clean_intro_text()

    def test_raises_validation_error_when_none(self):
        from home.models.pages.home_page import HomePageAdminForm

        form = HomePageAdminForm.__new__(HomePageAdminForm)
        form.cleaned_data = {"intro_text": None}
        with pytest.raises(forms.ValidationError):
            form.clean_intro_text()

    def test_returns_value_when_valid(self):
        from home.models.pages.home_page import HomePageAdminForm

        form = HomePageAdminForm.__new__(HomePageAdminForm)
        form.cleaned_data = {"intro_text": "Welcome!"}
        result = form.clean_intro_text()
        assert result == "Welcome!"


class TestHomePageGetContext:
    def _make_card_block(self, start_date=None, end_date=None):
        block = MagicMock()
        block.value.get = lambda k, default=None: {
            "start_date": start_date,
            "end_date": end_date,
        }.get(k, default)
        return block

    def test_includes_live_cards_with_no_dates(self):
        from home.models.pages.home_page import HomePage

        page = MagicMock(spec=HomePage)
        card = self._make_card_block()
        page.static_text_cards = [card]

        mock_request = MagicMock()
        mock_context = {}

        with (
            patch(
                "home.models.pages.home_page.Page.get_context",
                return_value=mock_context,
            ),
            patch(
                "home.models.pages.home_page.NewsItem.objects.live",
            ) as mock_live,
            patch(
                "home.models.pages.home_page.PressReleasePage.objects.live",
            ) as mock_pr_live,
        ):
            mock_qs = MagicMock()
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_live.return_value = mock_qs

            mock_pr_live.return_value.first.return_value = None

            result = HomePage.get_context(page, mock_request)

        assert "live_static_text_cards" in result
        assert len(result["live_static_text_cards"]) == 1

    def test_excludes_card_not_yet_started(self):
        from home.models.pages.home_page import HomePage

        page = MagicMock(spec=HomePage)
        future = timezone.now() + timedelta(days=10)
        card = self._make_card_block(start_date=future)
        page.static_text_cards = [card]

        mock_context = {}

        with (
            patch(
                "home.models.pages.home_page.Page.get_context",
                return_value=mock_context,
            ),
            patch("home.models.pages.home_page.NewsItem.objects.live") as mock_live,
            patch(
                "home.models.pages.home_page.PressReleasePage.objects.live"
            ) as mock_pr_live,
        ):
            mock_qs = MagicMock()
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_live.return_value = mock_qs
            mock_pr_live.return_value.first.return_value = None

            result = HomePage.get_context(page, MagicMock())

        assert result["live_static_text_cards"] == []

    def test_excludes_card_already_expired(self):
        from home.models.pages.home_page import HomePage

        page = MagicMock(spec=HomePage)
        past = timezone.now() - timedelta(days=5)
        card = self._make_card_block(end_date=past)
        page.static_text_cards = [card]

        mock_context = {}

        with (
            patch(
                "home.models.pages.home_page.Page.get_context",
                return_value=mock_context,
            ),
            patch("home.models.pages.home_page.NewsItem.objects.live") as mock_live,
            patch(
                "home.models.pages.home_page.PressReleasePage.objects.live"
            ) as mock_pr_live,
        ):
            mock_qs = MagicMock()
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_live.return_value = mock_qs
            mock_pr_live.return_value.first.return_value = None

            result = HomePage.get_context(page, MagicMock())

        assert result["live_static_text_cards"] == []

    def test_sets_press_release_url_when_found(self):
        from home.models.pages.home_page import HomePage

        page = MagicMock(spec=HomePage)
        page.static_text_cards = []
        mock_context = {}

        mock_pr = MagicMock()
        mock_pr.url = "/news/"

        with (
            patch(
                "home.models.pages.home_page.Page.get_context",
                return_value=mock_context,
            ),
            patch("home.models.pages.home_page.NewsItem.objects.live") as mock_live,
            patch(
                "home.models.pages.home_page.PressReleasePage.objects.live"
            ) as mock_pr_live,
        ):
            mock_qs = MagicMock()
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_live.return_value = mock_qs
            mock_pr_live.return_value.first.return_value = mock_pr

            result = HomePage.get_context(page, MagicMock())

        assert result["press_release_page_url"] == "/news/"

    def test_sets_fallback_press_release_url_when_not_found(self):
        from home.models.pages.home_page import HomePage

        page = MagicMock(spec=HomePage)
        page.static_text_cards = []
        mock_context = {}

        with (
            patch(
                "home.models.pages.home_page.Page.get_context",
                return_value=mock_context,
            ),
            patch("home.models.pages.home_page.NewsItem.objects.live") as mock_live,
            patch(
                "home.models.pages.home_page.PressReleasePage.objects.live"
            ) as mock_pr_live,
        ):
            mock_qs = MagicMock()
            mock_qs.filter.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_live.return_value = mock_qs
            mock_pr_live.return_value.first.return_value = None

            result = HomePage.get_context(page, MagicMock())

        assert result["press_release_page_url"] == "/news-and-announcements/"
