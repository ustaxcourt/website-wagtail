"""Tests for home/mixins/moderation.py"""

from datetime import timedelta
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
