"""Tests for home/mixins/moderation.py"""

from datetime import timedelta

import pytest
from unittest.mock import MagicMock, patch
from django.utils import timezone

from home.mixins.moderation import ModerationMixin


class ConcreteModerationMixin(ModerationMixin):
    """A concrete (non-abstract) version for testing non-DB properties."""

    class Meta:
        app_label = "home"
        # Not abstract so we can instantiate
        abstract = True


class TestModerationMixinCleanLogic:
    """Test the clean() method logic of ModerationMixin using a mock."""

    def test_get_moderation_panels_returns_list(self):
        from home.mixins.moderation import ModerationMixin

        # get_moderation_panels is a classmethod
        panels = ModerationMixin.get_moderation_panels()
        assert isinstance(panels, list)
        assert len(panels) == 2

    def test_on_workflow_cancelled_clears_review_by(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock(spec=ModerationMixin)
        obj.review_by = timezone.now()
        obj.save = MagicMock()
        # Call the method directly on the mock
        ModerationMixin.on_workflow_cancelled(obj)
        assert obj.review_by is None
        obj.save.assert_called_once()

    def test_on_workflow_approved_clears_review_by(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock(spec=ModerationMixin)
        obj.review_by = timezone.now()
        obj.save = MagicMock()
        ModerationMixin.on_workflow_approved(obj)
        assert obj.review_by is None
        obj.save.assert_called_once()


class TestModerationMixinIsReviewOverdue:
    """Test the is_review_overdue property through ModerationMixin directly."""

    def test_is_review_overdue_false_when_no_review_by(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock()
        obj.review_by = None
        result = ModerationMixin.is_review_overdue.fget(obj)
        assert result is False

    def test_is_review_overdue_true_when_past(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock()
        obj.review_by = timezone.now() - timedelta(days=1)
        result = ModerationMixin.is_review_overdue.fget(obj)
        assert result is True

    def test_is_review_overdue_false_when_future(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock()
        obj.review_by = timezone.now() + timedelta(days=1)
        result = ModerationMixin.is_review_overdue.fget(obj)
        assert result is False

    def test_is_review_overdue_with_naive_datetime(self):
        from home.mixins.moderation import ModerationMixin
        from datetime import datetime as dt

        obj = MagicMock()
        obj.review_by = dt(2020, 1, 1, 0, 0, 0)  # naive past date
        result = ModerationMixin.is_review_overdue.fget(obj)
        assert result is True


class TestModerationMixinDaysUntilReview:
    def test_days_until_review_none_when_no_review_by(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock()
        obj.review_by = None
        result = ModerationMixin.days_until_review.fget(obj)
        assert result is None

    def test_days_until_review_positive_when_future(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock()
        obj.review_by = timezone.now() + timedelta(days=5)
        result = ModerationMixin.days_until_review.fget(obj)
        assert result >= 4

    def test_days_until_review_negative_when_past(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock()
        obj.review_by = timezone.now() - timedelta(days=3)
        result = ModerationMixin.days_until_review.fget(obj)
        assert result < 0


class TestModerationMixinSaveRevision:
    """Test save_revision method coverage."""

    def test_save_revision_with_string_review_by(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock(spec=ModerationMixin)
        obj.review_by = None

        mock_revision = MagicMock()
        mock_revision.content.get.return_value = "2025-01-01T10:00:00"

        with patch("home.mixins.moderation.super") as mock_super:
            mock_super_instance = MagicMock()
            mock_super_instance.save_revision.return_value = mock_revision
            mock_super.return_value = mock_super_instance

            ModerationMixin.save_revision(obj, clean=True)
            # Just verify it ran through without raising

    def test_save_revision_with_no_review_by_in_revision(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock(spec=ModerationMixin)
        obj.review_by = None

        mock_revision = MagicMock()
        mock_revision.content.get.return_value = None

        with patch("home.mixins.moderation.super") as mock_super:
            mock_super_instance = MagicMock()
            mock_super_instance.save_revision.return_value = mock_revision
            mock_super.return_value = mock_super_instance

            ModerationMixin.save_revision(obj, clean=True)

    def test_on_workflow_cancelled_without_review_by_attr(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock(spec=[])  # no attributes
        # Should not raise
        ModerationMixin.on_workflow_cancelled(obj)

    def test_on_workflow_approved_without_review_by_attr(self):
        from home.mixins.moderation import ModerationMixin

        obj = MagicMock(spec=[])  # no attributes
        # Should not raise
        ModerationMixin.on_workflow_approved(obj)


@pytest.mark.django_db
class TestModerationMixinWithRealModel:
    """Integration-style tests using Banner, which includes ModerationMixin."""

    def _banner(self, **kwargs):
        from home.models.snippets.banners import Banner

        defaults = dict(
            banner_title="B",
            description="D",
            priority_level="high",
            banner_start_date=timezone.now() - timedelta(days=30),
        )
        defaults.update(kwargs)
        return Banner.objects.create(**defaults)

    def test_save_revision_propagates_review_by_to_live_row(self):
        banner = self._banner()
        review_by = (timezone.now() + timedelta(days=3)).replace(microsecond=0)
        banner.review_by = review_by
        revision = banner.save_revision()

        assert revision is not None
        banner.refresh_from_db()
        assert banner.review_by == review_by

    def test_save_revision_clears_review_by_when_absent_from_revision(self):
        banner = self._banner(review_by=timezone.now() + timedelta(days=1))
        banner.review_by = None
        banner.save_revision()

        banner.refresh_from_db()
        assert banner.review_by is None

    def test_save_revision_accepts_clean_false(self):
        # Invalid banner (high priority, no start date) must not raise
        # when the caller opts out of validation.
        banner = self._banner()
        banner.priority_level = "high"
        banner.banner_start_date = None
        assert banner.save_revision(clean=False) is not None

    def test_save_revision_runs_clean_by_default(self):
        from django.core.exceptions import ValidationError

        banner = self._banner()
        banner.priority_level = "high"
        banner.banner_start_date = None
        with pytest.raises(ValidationError):
            banner.save_revision()

    def test_on_workflow_cancelled_persists_cleared_review_by(self):
        banner = self._banner(review_by=timezone.now() + timedelta(days=1))
        banner.on_workflow_cancelled()
        banner.refresh_from_db()
        assert banner.review_by is None

    def test_on_workflow_approved_persists_cleared_review_by(self):
        banner = self._banner(review_by=timezone.now() + timedelta(days=1))
        banner.on_workflow_approved()
        banner.refresh_from_db()
        assert banner.review_by is None

    def test_latest_revision_object_uses_review_by_from_revision(self):
        banner = self._banner()
        review_by = (timezone.now() + timedelta(days=5)).replace(microsecond=0)
        banner.review_by = review_by
        banner.save_revision()
        # Live row diverges from the revision.
        type(banner).objects.filter(pk=banner.pk).update(review_by=None)
        banner.refresh_from_db()

        obj = banner.get_latest_revision_as_object()
        assert obj.review_by == review_by
        assert obj._skip_review_by_validation is True

    def test_latest_revision_object_falls_back_to_live_review_by(self):
        banner = self._banner()
        banner.save_revision()  # revision has review_by = None
        live_value = timezone.now() + timedelta(days=2)
        type(banner).objects.filter(pk=banner.pk).update(review_by=live_value)
        banner.refresh_from_db()

        obj = banner.get_latest_revision_as_object()
        assert obj.review_by == live_value

    def test_latest_revision_object_without_revisions(self):
        banner = self._banner()
        obj = banner.get_latest_revision_as_object()
        assert obj._skip_review_by_validation is True

    def test_latest_revision_object_falls_back_when_revision_lookup_fails(self):
        banner = self._banner(review_by=timezone.now() + timedelta(days=1))
        banner.save_revision()
        broken = MagicMock()
        broken.exists.return_value = True
        broken.latest.side_effect = Exception("boom")
        with patch.object(
            type(banner), "revisions", new_callable=lambda: property(lambda s: broken)
        ):
            obj = banner.get_latest_revision_as_object()
        assert obj.review_by == banner.review_by
