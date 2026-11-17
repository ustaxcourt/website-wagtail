"""Tests for home/models/snippets/banners.py"""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock, PropertyMock
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


@pytest.mark.django_db
class TestBannerOverlapDatabase:
    """Exercise _check_banner_overlap / clean() against real rows."""

    def _create(
        self, title="Existing", priority="high", start=None, end=None, live=True
    ):
        return Banner.objects.create(
            banner_title=title,
            description="Desc",
            priority_level=priority,
            banner_start_date=start,
            banner_end_date=end,
            live=live,
        )

    def _candidate(self, priority="high", start=None, end=None, title="New"):
        return Banner(
            banner_title=title,
            description="Desc",
            priority_level=priority,
            banner_start_date=start,
            banner_end_date=end,
        )

    def test_other_indefinite_and_self_indefinite_overlaps(self):
        now = timezone.now()
        self._create(start=now)
        with pytest.raises(ValidationError) as exc:
            self._candidate(start=now + timedelta(days=1))._check_banner_overlap("high")
        message = str(exc.value.message_dict["banner_start_date"])
        assert "indefinite" in message
        assert "Existing" in message

    def test_other_indefinite_starts_before_self_ends_overlaps(self):
        now = timezone.now()
        self._create(start=now)
        candidate = self._candidate(start=now, end=now + timedelta(days=2))
        with pytest.raises(ValidationError):
            candidate._check_banner_overlap("high")

    def test_other_indefinite_starts_after_self_ends_no_overlap(self):
        now = timezone.now()
        self._create(start=now + timedelta(days=10))
        candidate = self._candidate(start=now, end=now + timedelta(days=2))
        candidate._check_banner_overlap("high")

    def test_self_indefinite_other_ends_after_self_starts_overlaps(self):
        now = timezone.now()
        self._create(start=now, end=now + timedelta(days=5))
        candidate = self._candidate(start=now + timedelta(days=1))
        with pytest.raises(ValidationError) as exc:
            candidate._check_banner_overlap("high")
        # Finite end date is rendered, not "indefinite"
        assert "indefinite" not in str(exc.value.message_dict["banner_start_date"])

    def test_self_indefinite_other_ended_before_self_starts_no_overlap(self):
        now = timezone.now()
        self._create(start=now - timedelta(days=10), end=now - timedelta(days=5))
        self._candidate(start=now)._check_banner_overlap("high")

    def test_both_bounded_overlapping_raises(self):
        now = timezone.now()
        self._create(start=now, end=now + timedelta(days=5))
        candidate = self._candidate(
            start=now + timedelta(days=2), end=now + timedelta(days=8)
        )
        with pytest.raises(ValidationError):
            candidate._check_banner_overlap("high")

    def test_both_bounded_disjoint_no_overlap(self):
        now = timezone.now()
        self._create(start=now, end=now + timedelta(days=5))
        candidate = self._candidate(
            start=now + timedelta(days=6), end=now + timedelta(days=8)
        )
        candidate._check_banner_overlap("high")

    def test_different_priority_ignored(self):
        now = timezone.now()
        self._create(priority="critical", start=now)
        self._candidate(priority="high", start=now)._check_banner_overlap("high")

    def test_non_live_banner_ignored(self):
        now = timezone.now()
        self._create(start=now, live=False)
        self._candidate(start=now)._check_banner_overlap("high")

    def test_banner_does_not_overlap_itself(self):
        now = timezone.now()
        existing = self._create(start=now)
        existing._check_banner_overlap("high")

    def test_clean_raises_on_overlap(self):
        now = timezone.now()
        self._create(start=now)
        with pytest.raises(ValidationError) as exc:
            self._candidate(start=now).clean()
        assert "banner_start_date" in exc.value.message_dict

    def test_clean_passes_for_valid_banner(self):
        self._candidate(start=timezone.now()).clean()

    def test_clean_requires_title(self):
        banner = self._candidate(start=timezone.now(), title="")
        with pytest.raises(ValidationError) as exc:
            banner.clean()
        assert "banner_title" in exc.value.message_dict

    def test_clean_requires_description(self):
        banner = self._candidate(start=timezone.now())
        banner.description = ""
        with pytest.raises(ValidationError) as exc:
            banner.clean()
        assert "description" in exc.value.message_dict


@pytest.mark.django_db
class TestBannerQuerySetAndProperties:
    def _create(self, **kwargs):
        defaults = dict(banner_title="B", description="D", priority_level="high")
        defaults.update(kwargs)
        return Banner.objects.create(**defaults)

    def test_live_includes_started_unexpired_banner(self):
        banner = self._create(
            live=True, banner_start_date=timezone.now() - timedelta(hours=1)
        )
        assert banner in Banner.objects.live()

    def test_live_excludes_not_yet_started(self):
        banner = self._create(
            live=True, banner_start_date=timezone.now() + timedelta(days=1)
        )
        assert banner not in Banner.objects.live()

    def test_live_excludes_expired(self):
        banner = self._create(
            live=True,
            banner_start_date=timezone.now() - timedelta(days=2),
            expire_at=timezone.now() - timedelta(days=1),
        )
        assert banner not in Banner.objects.live()

    def test_live_excludes_draft(self):
        banner = self._create(
            live=False, banner_start_date=timezone.now() - timedelta(hours=1)
        )
        assert banner not in Banner.objects.live()

    def test_live_includes_future_expiry(self):
        banner = self._create(
            live=True,
            banner_start_date=timezone.now() - timedelta(days=1),
            expire_at=timezone.now() + timedelta(days=1),
        )
        assert banner in Banner.objects.live()

    def test_simple_properties(self):
        start = timezone.now()
        end = start + timedelta(days=1)
        banner = self._create(banner_start_date=start, banner_end_date=end)
        assert banner.title == "B"
        assert banner.publish_date == start
        assert banner.homepage_display_expiration_date == end
        assert list(banner.revisions.all()) == list(banner._revisions.all()) == []

    def test_document_url_dash_without_document(self):
        assert self._create().document_url == "-"

    def test_document_url_with_document(self):
        banner = Banner(banner_title="B")
        with patch.object(
            Banner, "document", new_callable=PropertyMock
        ) as mock_document:
            mock_document.return_value = MagicMock(url="/documents/1/banner.pdf")
            assert banner.document_url == "/documents/1/banner.pdf"

    def test_document_url_dash_when_document_has_no_url(self):
        banner = Banner(banner_title="B")
        banner.document = None
        assert banner.document_url == "-"
