"""Tests for home/signals.py"""

from unittest.mock import MagicMock
from django.utils import timezone


class TestClearReviewByOnWorkflowCancelled:
    def test_clears_review_by_when_instance_has_it(self):
        """Signal should clear review_by on a ModerationMixin instance."""
        from home.signals import clear_review_by_on_workflow_cancelled
        from home.mixins.moderation import ModerationMixin

        instance = MagicMock(spec=ModerationMixin)
        instance.review_by = timezone.now()

        clear_review_by_on_workflow_cancelled(sender=None, instance=instance)

        assert instance.review_by is None
        instance.save.assert_called_once_with(update_fields=["review_by"])

    def test_no_op_when_review_by_is_none(self):
        """Signal should not save when review_by is already None."""
        from home.signals import clear_review_by_on_workflow_cancelled
        from home.mixins.moderation import ModerationMixin

        instance = MagicMock(spec=ModerationMixin)
        instance.review_by = None

        clear_review_by_on_workflow_cancelled(sender=None, instance=instance)

        instance.save.assert_not_called()

    def test_no_op_when_instance_is_none(self):
        """Signal should not call save when instance is None."""
        from home.signals import clear_review_by_on_workflow_cancelled
        from home.mixins.moderation import ModerationMixin
        from unittest.mock import patch

        with patch.object(ModerationMixin, "save") as mock_save:
            clear_review_by_on_workflow_cancelled(sender=None, instance=None)
            mock_save.assert_not_called()

    def test_no_op_when_instance_not_moderation_mixin(self):
        """Signal should not touch non-ModerationMixin objects."""
        from home.signals import clear_review_by_on_workflow_cancelled

        # Not an instance of ModerationMixin, so spec doesn't inherit it
        # Use a plain object
        class PlainModel:
            review_by = timezone.now()

            def save(self, **kwargs):
                pass

        plain = PlainModel()
        # Should silently skip (isinstance check fails)
        clear_review_by_on_workflow_cancelled(sender=None, instance=plain)
        # review_by was not cleared
        assert plain.review_by is not None


class TestClearReviewByOnWorkflowApproved:
    def test_clears_review_by_when_instance_has_it(self):
        from home.signals import clear_review_by_on_workflow_approved
        from home.mixins.moderation import ModerationMixin

        instance = MagicMock(spec=ModerationMixin)
        instance.review_by = timezone.now()

        clear_review_by_on_workflow_approved(sender=None, instance=instance)

        assert instance.review_by is None
        instance.save.assert_called_once_with(update_fields=["review_by"])

    def test_no_op_when_review_by_is_none(self):
        from home.signals import clear_review_by_on_workflow_approved
        from home.mixins.moderation import ModerationMixin

        instance = MagicMock(spec=ModerationMixin)
        instance.review_by = None

        clear_review_by_on_workflow_approved(sender=None, instance=instance)

        instance.save.assert_not_called()

    def test_no_op_when_instance_is_none(self):
        from home.signals import clear_review_by_on_workflow_approved
        from home.mixins.moderation import ModerationMixin
        from unittest.mock import patch

        with patch.object(ModerationMixin, "save") as mock_save:
            clear_review_by_on_workflow_approved(sender=None, instance=None)
            mock_save.assert_not_called()
