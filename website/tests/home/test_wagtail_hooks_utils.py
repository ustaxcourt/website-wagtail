"""Tests for utility functions in home/wagtail_hooks.py"""

import pytest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory, override_settings

from home.wagtail_hooks import (
    environment_is_prod,
    purge_cloudflare_root,
    ConditionalRoleSwitcherMenuItem,
)
from app.role_switcher.views import (
    SESSION_IS_ASSUMING_ROLE_KEY,
    SESSION_ORIGINAL_IS_SUPERUSER_KEY,
)


class TestEnvironmentIsProd:
    @override_settings(ENVIRONMENT="production")
    def test_returns_true_for_production(self):
        assert environment_is_prod() is True

    @override_settings(ENVIRONMENT="staging")
    def test_returns_false_for_non_production(self):
        assert environment_is_prod() is False

    def test_returns_false_when_setting_missing(self):
        from django.conf import settings

        if hasattr(settings, "ENVIRONMENT"):
            with override_settings(ENVIRONMENT=None):
                # None is falsy but doesn't raise AttributeError
                assert environment_is_prod() is False
        else:
            assert environment_is_prod() is False


class TestPurgeCloudflareRoot:
    def test_returns_true_on_success(self):
        mock_batch = MagicMock()
        with patch("home.wagtail_hooks.PurgeBatch", return_value=mock_batch):
            result = purge_cloudflare_root()
        assert result is True
        mock_batch.add_url.assert_called_once_with("/*")
        mock_batch.purge.assert_called_once()

    def test_returns_false_on_exception(self):
        with patch("home.wagtail_hooks.PurgeBatch", side_effect=Exception("boom")):
            result = purge_cloudflare_root()
        assert result is False


@pytest.mark.django_db
class TestConditionalRoleSwitcherMenuItemIsShown:
    def _make_menu_item(self):
        return ConditionalRoleSwitcherMenuItem("Role Switcher", "/switch-role/")

    def _make_request(self, is_superuser=False, session=None):
        factory = RequestFactory()
        request = factory.get("/")
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = is_superuser
        request.user = user
        request.session = session or {}
        return request

    @override_settings(ENVIRONMENT="production")
    def test_hidden_in_production(self):
        item = self._make_menu_item()
        request = self._make_request(is_superuser=True)
        assert item.is_shown(request) is False

    @override_settings(ENVIRONMENT="staging")
    def test_shown_for_superuser(self):
        item = self._make_menu_item()
        request = self._make_request(is_superuser=True)
        assert item.is_shown(request) is True

    @override_settings(ENVIRONMENT="staging")
    def test_hidden_for_non_superuser(self):
        item = self._make_menu_item()
        request = self._make_request(is_superuser=False)
        assert item.is_shown(request) is False

    @override_settings(ENVIRONMENT="staging")
    def test_shown_when_assuming_role_and_was_superuser(self):
        item = self._make_menu_item()
        session = {
            SESSION_IS_ASSUMING_ROLE_KEY: True,
            SESSION_ORIGINAL_IS_SUPERUSER_KEY: True,
        }
        request = self._make_request(is_superuser=False, session=session)
        assert item.is_shown(request) is True

    @override_settings(ENVIRONMENT="staging")
    def test_hidden_when_assuming_role_but_was_not_superuser(self):
        item = self._make_menu_item()
        session = {
            SESSION_IS_ASSUMING_ROLE_KEY: True,
            SESSION_ORIGINAL_IS_SUPERUSER_KEY: False,
        }
        request = self._make_request(is_superuser=False, session=session)
        assert item.is_shown(request) is False
