"""Tests for app/context_processors.py"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, override_settings

from app.context_processors import (
    build_info,
    _get_timezone_offset_ms,
    yellow_priority_news,
    critical_priority_news,
)


class TestBuildInfo:
    @override_settings(GITHUB_SHA="abcdef1234567890")
    def test_returns_shortened_sha(self):
        request = RequestFactory().get("/")
        result = build_info(request)
        assert result["build_sha"] == "abcdef1"

    @override_settings(GITHUB_SHA="abc")
    def test_returns_short_sha_as_is(self):
        request = RequestFactory().get("/")
        result = build_info(request)
        assert result["build_sha"] == "abc"


class TestGetTimezoneOffsetMs:
    @override_settings(TIME_ZONE="UTC")
    def test_returns_zero_for_utc(self):
        result = _get_timezone_offset_ms()
        assert result == 0

    @override_settings(TIME_ZONE="America/New_York")
    def test_returns_integer(self):
        result = _get_timezone_offset_ms()
        assert isinstance(result, int)


@pytest.mark.django_db
class TestYellowPriorityNews:
    def test_returns_context_keys(self):
        request = RequestFactory().get("/")
        with patch("app.context_processors.Banner") as mock_banner:
            mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = []
            result = yellow_priority_news(request)
        assert "yellow_priority_news_json" in result
        assert "has_yellow_news" in result
        assert result["has_yellow_news"] is False

    def test_has_yellow_news_true_when_banners_exist(self):
        request = RequestFactory().get("/")
        mock_item = MagicMock()
        mock_item.id = 1
        mock_item.banner_title = "Alert"
        mock_item.description = "desc"
        mock_item.priority_level = "high"
        mock_item.document = None
        mock_item.banner_start_date = None
        mock_item.banner_end_date = None
        with patch("app.context_processors.Banner") as mock_banner:
            mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = [
                mock_item
            ]
            result = yellow_priority_news(request)
        assert result["has_yellow_news"] is True


@pytest.mark.django_db
class TestCriticalPriorityNews:
    def test_returns_context_keys(self):
        request = RequestFactory().get("/")
        with patch("app.context_processors.Banner") as mock_banner:
            mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = []
            result = critical_priority_news(request)
        assert "critical_priority_news_json" in result
        assert "has_critical_news" in result
        assert result["has_critical_news"] is False
