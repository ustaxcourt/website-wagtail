"""Tests for home/models/pages/press_release.py"""

import pytest
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
        """NewsItem with a document is grouped by year with details.file set."""
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
                entry = result[year][0]
                assert entry["is_news_item"] is True
                assert entry["details"]["description"] == "Test Release"
                assert entry["details"]["file"] is news_item.document

    def test_groups_news_items_without_document_by_year(self):
        """NewsItem without a document is grouped as a homepage entry with title and body."""
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
                assert entry["is_homepage_entry"] is True
                assert entry["title"] == "No Doc Release"
                assert entry["body"] == "Some body"
                assert entry["id"] == 2
                assert entry["file"] is None

    @pytest.mark.parametrize(
        "priority_level, expected_label",
        [
            ("high", "High Priority"),
            ("critical", "Critical"),
        ],
    )
    def test_groups_banners_by_year_with_correct_label(
        self, priority_level, expected_label
    ):
        """Banners are grouped by year and labelled according to their priority level."""
        page = self._make_page()

        now = timezone.now()
        banner = MagicMock()
        banner.banner_start_date = now
        banner.priority_level = priority_level
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
                assert entry["banner_label"] == expected_label
                assert entry["banner_type"] == priority_level

    def test_news_item_with_none_publish_date_is_skipped(self):
        page = self._make_page()

        news_item = MagicMock()
        news_item.publish_date = None
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

    def test_banner_with_none_start_date_is_skipped(self):
        page = self._make_page()

        banner = MagicMock()
        banner.banner_start_date = None

        with patch("home.models.pages.press_release.NewsItem") as mock_ni:
            mock_ni.objects.live.return_value.filter.return_value.order_by.return_value = []
            with patch("home.models.pages.press_release.Banner") as mock_banner:
                mock_banner.objects.live.return_value.filter.return_value.order_by.return_value = [
                    banner
                ]
                result = page.group_press_releases_by_year
                assert result == {}


class TestArchiveView:
    def _make_page(self):
        from home.models.pages.press_release import PressReleasePage

        obj = PressReleasePage.__new__(PressReleasePage)
        obj.title = "News and Announcements"
        obj.template = "home/news_announcements_page.html"
        return obj

    def test_archive_view_shows_years_beyond_first_four(self):
        """archive_view exposes years 5+ and excludes the four most recent years."""
        from django.test import RequestFactory

        page = self._make_page()
        request = RequestFactory().get("/news/archives/")

        grouped = {
            2024: [{"release_date": "2024-01-01"}],
            2023: [{"release_date": "2023-01-01"}],
            2022: [{"release_date": "2022-01-01"}],
            2021: [{"release_date": "2021-01-01"}],
            2020: [{"release_date": "2020-01-01"}],
        }

        mock_context = {"page": page, "press_releases_by_year": {}}

        with patch.object(
            type(page),
            "group_press_releases_by_year",
            new_callable=lambda: property(lambda s: grouped),
        ):
            with patch.object(page, "get_context", return_value=mock_context):
                response = page.archive_view(request)

        ctx = response.context_data
        assert ctx["is_archive"] is True
        assert response.template_name == page.template
        assert 2020 in ctx["press_releases_by_year"]
        for recent_year in [2024, 2023, 2022, 2021]:
            assert recent_year not in ctx["press_releases_by_year"]


class TestGetContext:
    def _make_page(self):
        from home.models.pages.press_release import PressReleasePage

        obj = PressReleasePage.__new__(PressReleasePage)
        return obj

    def test_get_context_includes_only_first_four_years(self):
        """get_context limits press_releases_by_year to the four most recent years."""
        from django.test import RequestFactory

        page = self._make_page()
        request = RequestFactory().get("/news/")

        grouped = {
            2024: [],
            2023: [],
            2022: [],
            2021: [],
            2020: [],
        }

        with patch.object(
            type(page),
            "group_press_releases_by_year",
            new_callable=lambda: property(lambda s: grouped),
        ):
            with patch(
                "home.models.pages.press_release.EnhancedStandardPage.get_context",
                return_value={},
            ):
                context = page.get_context(request)

        assert context["is_archive"] is False
        for recent_year in [2024, 2023, 2022, 2021]:
            assert recent_year in context["press_releases_by_year"]
        assert 2020 not in context["press_releases_by_year"]
