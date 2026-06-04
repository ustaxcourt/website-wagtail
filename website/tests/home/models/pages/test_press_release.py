"""Tests for home/models/pages/press_release.py"""

from unittest.mock import patch, MagicMock
from django.utils import timezone


class TestGroupPressReleasesByYear:
    """Test the group_press_releases_by_year property."""

    def _make_page(self):
        from home.models.pages.press_release import PressReleasePage

        obj = PressReleasePage.__new__(PressReleasePage)
        return obj

    def test_returns_empty_dict_when_no_items(self):
        page = self._make_page()

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = []
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = []
                result = page.group_press_releases_by_year
                assert result == {}

    def test_groups_news_items_with_document_by_year(self):
        page = self._make_page()

        now = timezone.now()
        news_item = MagicMock()
        news_item.publish_date = now
        news_item.document = MagicMock()
        news_item.title = "Test Release"
        news_item.id = 1

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = [
                news_item
            ]
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = []
                result = page.group_press_releases_by_year
                year = now.year
                assert year in result
                assert len(result[year]) == 1
                assert result[year][0]["is_news_item"] is True

    def test_groups_news_items_without_document_by_year(self):
        page = self._make_page()

        now = timezone.now()
        news_item = MagicMock()
        news_item.publish_date = now
        news_item.document = None
        news_item.title = "No Doc Release"
        news_item.description = "Some body"
        news_item.id = 2

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = [
                news_item
            ]
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = []
                result = page.group_press_releases_by_year
                year = now.year
                assert year in result
                entry = result[year][0]
                assert entry.get("is_homepage_entry") is True

    def test_groups_banners_by_year(self):
        page = self._make_page()

        now = timezone.now()
        banner = MagicMock()
        banner.banner_start_date = now
        banner.priority_level = "high"
        banner.banner_title = "Important Banner"
        banner.description = "Details"
        banner.document = None

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = []
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = [
                    banner
                ]
                result = page.group_press_releases_by_year
                year = now.year
                assert year in result
                entry = result[year][0]
                assert entry["is_banner"] is True
                assert entry["banner_label"] == "High Priority"

    def test_banner_critical_priority_label(self):
        page = self._make_page()

        now = timezone.now()
        banner = MagicMock()
        banner.banner_start_date = now
        banner.priority_level = "critical"
        banner.banner_title = "Critical"
        banner.description = "Details"
        banner.document = None

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = []
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = [
                    banner
                ]
                result = page.group_press_releases_by_year
                year = now.year
                entry = result[year][0]
                assert entry["banner_label"] == "Critical"

    def test_news_item_with_none_publish_date_is_skipped(self):
        page = self._make_page()

        news_item = MagicMock()
        news_item.publish_date = None  # no date
        news_item.document = None
        news_item.title = "No Date"

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = [
                news_item
            ]
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = []
                result = page.group_press_releases_by_year
                assert result == {}
