"""Tests for home/models/snippets/banners.py"""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.utils import timezone
from django.forms import ValidationError

from home.models.snippets.banners import Banner


class TestBannerCategory:
    def _make_banner(self, priority_level):
        obj = Banner.__new__(Banner)
        obj.priority_level = priority_level
        return obj

    def test_high_priority_category(self):
        banner = self._make_banner("high")
        assert banner.category == "High Priority"

    def test_critical_priority_category(self):
        banner = self._make_banner("critical")
        assert banner.category == "Critical"

    def test_other_priority_category(self):
        banner = self._make_banner("none")
        assert banner.category == "None"

    def test_str_returns_banner_title(self):
        obj = Banner.__new__(Banner)
        obj.banner_title = "Test Banner"
        assert str(obj) == "Test Banner"


class TestBannerCheckOverlapLogic:
    """Test _check_banner_overlap logic using mock querysets."""

    def _make_banner(self, priority="high", start_date=None, end_date=None, pk=1):
        obj = Banner.__new__(Banner)
        obj.id = pk
        obj.priority_level = priority
        obj.banner_start_date = start_date or timezone.now()
        obj.banner_end_date = end_date
        obj.banner_title = "Test Banner"
        return obj

    def test_no_overlap_when_no_other_banners(self):
        banner = self._make_banner()
        with patch.object(Banner, "objects") as mock_mgr:
            mock_mgr.filter.return_value.exclude.return_value.filter.return_value = []
            # Should not raise
            banner._check_banner_overlap("high")

    def test_overlap_when_other_banner_indefinite_and_this_also_indefinite(self):
        now = timezone.now()
        banner = self._make_banner(start_date=now, end_date=None, pk=2)

        other = MagicMock()
        other.banner_start_date = now - timedelta(hours=1)
        other.banner_end_date = None
        other.banner_title = "Existing Banner"

        with patch.object(Banner, "objects") as mock_mgr:
            mock_mgr.filter.return_value.exclude.return_value.filter.return_value = [
                other
            ]
            with pytest.raises(ValidationError):
                banner._check_banner_overlap("high")

    def test_no_overlap_when_other_banner_ends_before_this_starts(self):
        now = timezone.now()
        banner = self._make_banner(
            start_date=now + timedelta(hours=5),
            end_date=now + timedelta(hours=10),
            pk=2,
        )

        other = MagicMock()
        other.banner_start_date = now
        other.banner_end_date = now + timedelta(hours=3)  # ends before this one starts

        with patch.object(Banner, "objects") as mock_mgr:
            mock_mgr.filter.return_value.exclude.return_value.filter.return_value = [
                other
            ]
            # Should not raise
            banner._check_banner_overlap("high")


class TestBannerCleanValidation:
    def _make_banner(
        self, title="Test", description="Desc", priority="high", start_date=None
    ):
        obj = Banner.__new__(Banner)
        obj.id = 1
        obj.banner_title = title
        obj.description = description
        obj.priority_level = priority
        obj.banner_start_date = start_date
        obj.banner_end_date = None
        return obj

    def test_clean_missing_start_date_for_high_priority(self):
        banner = self._make_banner(priority="high", start_date=None)
        with patch.object(Banner, "clean", wraps=Banner.clean):
            with patch("home.models.snippets.banners.Banner._check_banner_overlap"):
                # Bypass the super().clean() call
                with patch("django.db.models.Model.clean"):
                    with pytest.raises(ValidationError) as exc_info:
                        Banner.clean(banner)
                    assert "banner_start_date" in exc_info.value.message_dict

    def test_clean_missing_start_date_for_critical_priority(self):
        banner = self._make_banner(priority="critical", start_date=None)
        with patch("django.db.models.Model.clean"):
            with pytest.raises(ValidationError) as exc_info:
                Banner.clean(banner)
            assert "banner_start_date" in exc_info.value.message_dict

    def test_clean_calls_overlap_check_when_start_date_set(self):
        banner = self._make_banner(priority="high", start_date=timezone.now())
        with patch("django.db.models.Model.clean"):
            with patch.object(banner, "_check_banner_overlap") as mock_check:
                with patch.object(Banner, "objects") as mock_mgr:
                    mock_mgr.filter.return_value.exclude.return_value.filter.return_value = []
                    Banner.clean(banner)
                    mock_check.assert_called_once_with("high")

    def test_category_property_accessed_from_banner(self):
        banner = self._make_banner(priority="high")
        assert banner.category == "High Priority"


class TestBannerPreview:
    """Test the multi-context preview support (preview_modes, get_preview_template,
    get_preview_context, as_press_release_entry)."""

    def _make_banner(self, priority="high", start_date=None):
        banner = Banner()
        banner.banner_title = "Important Banner"
        banner.description = "Details"
        banner.priority_level = priority
        banner.banner_start_date = start_date or timezone.now()
        banner.document = None
        return banner

    def test_preview_modes_exposes_banner_and_news_list(self):
        banner = self._make_banner()
        mode_names = [mode for mode, _ in banner.preview_modes]
        assert mode_names == ["banner", "news_list"]

    def test_get_preview_template_defaults_to_site_banner(self):
        banner = self._make_banner()
        assert (
            banner.get_preview_template(None, "banner")
            == "previews/banner_site_preview.html"
        )
        assert (
            banner.get_preview_template(None, "unknown")
            == "previews/banner_site_preview.html"
        )

    def test_get_preview_template_news_list_mode(self):
        banner = self._make_banner()
        assert (
            banner.get_preview_template(None, "news_list")
            == "previews/banner_news_list_preview.html"
        )

    def test_get_preview_context_includes_banner(self):
        banner = self._make_banner()
        context = banner.get_preview_context(None, "banner")
        assert context["banner"] is banner

    def test_get_preview_context_news_list_builds_grouped_entry(self):
        banner = self._make_banner(priority="critical")
        context = banner.get_preview_context(None, "news_list")
        year = banner.banner_start_date.year
        assert year in context["press_releases_by_year"]
        entry = context["press_releases_by_year"][year][0]
        assert entry["is_banner"] is True
        assert entry["banner_label"] == "Critical"

    def test_as_press_release_entry_matches_priority_label(self):
        banner = self._make_banner(priority="high")
        entry = banner.as_press_release_entry()
        assert entry["banner_label"] == "High Priority"
        assert entry["banner_title"] == "Important Banner"
        assert entry["release_date"] == banner.banner_start_date.date()

    def test_as_press_release_entry_handles_missing_start_date(self):
        banner = self._make_banner()
        banner.banner_start_date = None
        entry = banner.as_press_release_entry()
        assert entry["release_date"] is None
