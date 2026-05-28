"""Tests for home/forms.py — ReviewByRequiredOnSubmitSnippetForm._is_submit_for_moderation"""

from unittest.mock import patch
from django.utils import timezone

from home.forms import ReviewByRequiredOnSubmitSnippetForm


def make_form(post_data):
    """Create a minimal form instance with the given POST data."""
    form = ReviewByRequiredOnSubmitSnippetForm.__new__(
        ReviewByRequiredOnSubmitSnippetForm
    )
    form.data = post_data
    return form


class TestIsSubmitForModeration:
    def test_action_submit_key_returns_true(self):
        form = make_form({"action-submit": ""})
        assert form._is_submit_for_moderation() is True

    def test_action_submit_custom_suffix_returns_true(self):
        form = make_form({"action-submit-for-moderation": "Submit"})
        assert form._is_submit_for_moderation() is True

    def test_action_value_submit_returns_true(self):
        form = make_form({"action": "submit"})
        assert form._is_submit_for_moderation() is True

    def test_action_value_submit_for_moderation_returns_true(self):
        form = make_form({"action": "submit_for_moderation"})
        assert form._is_submit_for_moderation() is True

    def test_action_workflow_submit_value_returns_true(self):
        form = make_form({"action": "workflow-submit"})
        assert form._is_submit_for_moderation() is True

    def test_action_star_value_starts_with_submit_returns_true(self):
        form = make_form({"action-save": "submit_now"})
        assert form._is_submit_for_moderation() is True

    def test_workflow_action_submit_returns_true(self):
        form = make_form({"workflow-action": "submit"})
        assert form._is_submit_for_moderation() is True

    def test_transition_with_submit_returns_true(self):
        form = make_form({"transition": "submit_for_review"})
        assert form._is_submit_for_moderation() is True

    def test_submit_for_moderation_key_present_returns_true(self):
        form = make_form({"submit_for_moderation": ""})
        assert form._is_submit_for_moderation() is True

    def test_save_action_returns_false(self):
        form = make_form({"action-save": "Save draft"})
        assert form._is_submit_for_moderation() is False

    def test_empty_data_returns_false(self):
        form = make_form({})
        assert form._is_submit_for_moderation() is False

    def test_publish_action_returns_false(self):
        form = make_form({"action": "publish"})
        assert form._is_submit_for_moderation() is False


class TestReviewByRequiredOnSubmitPageForm:
    def test_page_form_action_submit_key_returns_true(self):
        from home.forms import ReviewByRequiredOnSubmitForm

        form = ReviewByRequiredOnSubmitForm.__new__(ReviewByRequiredOnSubmitForm)
        form.data = {"action-submit": ""}
        assert form._is_submit_for_moderation() is True

    def test_page_form_other_key_returns_false(self):
        from home.forms import ReviewByRequiredOnSubmitForm

        form = ReviewByRequiredOnSubmitForm.__new__(ReviewByRequiredOnSubmitForm)
        form.data = {"action-save": ""}
        assert form._is_submit_for_moderation() is False


class TestSnippetFormIsSubmitDebugPrints:
    """Test debug print branches in _is_submit_for_moderation (lines 24-34)."""

    def test_debug_true_prints_without_error(self):
        """With DEBUG=True the print statements execute."""
        from home.forms import ReviewByRequiredOnSubmitSnippetForm
        from django.test import override_settings

        with override_settings(DEBUG=True):
            form = ReviewByRequiredOnSubmitSnippetForm.__new__(
                ReviewByRequiredOnSubmitSnippetForm
            )
            form.data = {"action-submit": ""}
            result = form._is_submit_for_moderation()
        assert result is True

    def test_action_star_val_submit_for_moderation_returns_true(self):
        """action-* key with value 'submit_for_moderation' returns True."""
        from home.forms import ReviewByRequiredOnSubmitSnippetForm

        form = ReviewByRequiredOnSubmitSnippetForm.__new__(
            ReviewByRequiredOnSubmitSnippetForm
        )
        form.data = {"action-custom": "submit_for_moderation"}
        assert form._is_submit_for_moderation() is True


class TestSnippetFormClean:
    """Test clean() method of ReviewByRequiredOnSubmitSnippetForm."""

    def test_clean_not_submitting_skips_validation(self):
        from home.forms import ReviewByRequiredOnSubmitSnippetForm

        form = ReviewByRequiredOnSubmitSnippetForm.__new__(
            ReviewByRequiredOnSubmitSnippetForm
        )
        form.data = {"action-save": ""}

        cleaned = {"review_by": None}
        with patch(
            "wagtail.admin.forms.WagtailAdminModelForm.clean", return_value=cleaned
        ):
            result = form.clean()
        assert result == cleaned

    def test_clean_submitting_with_past_date_raises(self):
        from home.forms import ReviewByRequiredOnSubmitSnippetForm
        import datetime

        form = ReviewByRequiredOnSubmitSnippetForm.__new__(
            ReviewByRequiredOnSubmitSnippetForm
        )
        form.data = {"action-submit": ""}

        past_dt = timezone.now() - datetime.timedelta(hours=1)
        cleaned = {"review_by": past_dt}

        errors = {}
        form.add_error = lambda f, e: errors.update({f: e})

        with patch(
            "wagtail.admin.forms.WagtailAdminModelForm.clean", return_value=cleaned
        ):
            form.clean()

        assert "review_by" in errors

    def test_clean_submitting_with_future_date_no_error(self):
        from home.forms import ReviewByRequiredOnSubmitSnippetForm
        import datetime

        form = ReviewByRequiredOnSubmitSnippetForm.__new__(
            ReviewByRequiredOnSubmitSnippetForm
        )
        form.data = {"action-submit": ""}

        future_dt = timezone.now() + datetime.timedelta(hours=1)
        cleaned = {"review_by": future_dt}

        errors = {}
        form.add_error = lambda f, e: errors.update({f: e})

        with patch(
            "wagtail.admin.forms.WagtailAdminModelForm.clean", return_value=cleaned
        ):
            form.clean()

        assert "review_by" not in errors

    def test_clean_submitting_with_no_review_by_no_error(self):
        from home.forms import ReviewByRequiredOnSubmitSnippetForm

        form = ReviewByRequiredOnSubmitSnippetForm.__new__(
            ReviewByRequiredOnSubmitSnippetForm
        )
        form.data = {"action-submit": ""}

        cleaned = {"review_by": None}
        errors = {}
        form.add_error = lambda f, e: errors.update({f: e})

        with patch(
            "wagtail.admin.forms.WagtailAdminModelForm.clean", return_value=cleaned
        ):
            form.clean()

        assert "review_by" not in errors
