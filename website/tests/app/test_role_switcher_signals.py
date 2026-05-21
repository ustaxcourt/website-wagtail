"""Tests for app/role_switcher/signals.py"""

import pytest
from unittest.mock import MagicMock
from django.contrib.auth.models import User

from app.role_switcher.signals import revert_role_on_logout
from app.role_switcher.views import (
    SESSION_IS_ASSUMING_ROLE_KEY,
    SESSION_ORIGINAL_IS_SUPERUSER_KEY,
    SESSION_ORIGINAL_IS_STAFF_KEY,
    SESSION_ORIGINAL_GROUPS_KEY,
)


@pytest.mark.django_db
class TestRevertRoleOnLogout:
    def _make_user(self, superuser=False):
        return User.objects.create_user(
            username="tester",
            password="pw",
            is_superuser=superuser,
            is_staff=superuser,
        )

    def test_does_nothing_when_user_is_none(self):
        request = MagicMock()
        request.session = {}
        # Should not raise
        revert_role_on_logout(sender=None, request=request, user=None)

    def test_does_nothing_when_not_assuming_role(self):
        user = self._make_user()
        request = MagicMock()
        request.session = {SESSION_IS_ASSUMING_ROLE_KEY: False}
        revert_role_on_logout(sender=None, request=request, user=user)
        # User should remain unchanged
        user.refresh_from_db()
        assert not user.is_superuser

    def test_restores_superuser_on_logout_when_assuming_role(self):
        user = self._make_user(superuser=False)
        request = MagicMock()
        request.session = {
            SESSION_IS_ASSUMING_ROLE_KEY: True,
            SESSION_ORIGINAL_IS_SUPERUSER_KEY: True,
            SESSION_ORIGINAL_IS_STAFF_KEY: True,
            SESSION_ORIGINAL_GROUPS_KEY: [],
        }
        revert_role_on_logout(sender=None, request=request, user=user)
        user.refresh_from_db()
        assert user.is_superuser is True
        assert user.is_staff is True

    def test_does_nothing_when_not_originally_superuser(self):
        user = self._make_user(superuser=False)
        request = MagicMock()
        request.session = {
            SESSION_IS_ASSUMING_ROLE_KEY: True,
            SESSION_ORIGINAL_IS_SUPERUSER_KEY: False,
            SESSION_ORIGINAL_IS_STAFF_KEY: False,
            SESSION_ORIGINAL_GROUPS_KEY: [],
        }
        revert_role_on_logout(sender=None, request=request, user=user)
        user.refresh_from_db()
        assert not user.is_superuser
