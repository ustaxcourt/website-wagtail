"""Tests for home/management/commands/preregister_users.py"""

import json
import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import Group

from home.management.commands.preregister_users import Command


class TestGetUsersWithRolesFromSecret:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        cmd.style = MagicMock()
        cmd.style.ERROR = lambda s: s
        cmd.style.SUCCESS = lambda s: s
        cmd.style.WARNING = lambda s: s
        return cmd

    def test_returns_dict_when_secret_is_dict(self):
        cmd = self._make_cmd()
        data = {"Admin": ["a@example.com"]}
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            return_value=data,
        ):
            result = cmd.get_users_with_roles_from_secret()
        assert result == data

    def test_returns_dict_when_secret_is_json_string(self):
        cmd = self._make_cmd()
        data = {"Editor": ["editor@example.com"]}
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            return_value=json.dumps(data),
        ):
            result = cmd.get_users_with_roles_from_secret()
        assert result == data

    def test_returns_none_when_secret_is_none(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            return_value=None,
        ):
            result = cmd.get_users_with_roles_from_secret()
        assert result is None

    def test_returns_none_when_json_invalid(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            return_value="not-json",
        ):
            result = cmd.get_users_with_roles_from_secret()
        assert result is None

    def test_returns_none_when_runtime_error(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            side_effect=RuntimeError("AWS fail"),
        ):
            result = cmd.get_users_with_roles_from_secret()
        assert result is None

    def test_returns_none_when_unexpected_type(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            return_value=12345,
        ):
            result = cmd.get_users_with_roles_from_secret()
        assert result is None


@pytest.mark.django_db
class TestPreregisterUsersHandle:
    def _run(self, secret_data):
        cmd = Command()
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        with patch(
            "home.management.commands.preregister_users.get_secret_from_aws",
            return_value=secret_data,
        ):
            cmd.handle()

    def test_handle_with_none_secret_does_not_crash(self):
        self._run(None)

    def test_handle_with_valid_data_creates_users(self):
        Group.objects.get_or_create(name="Editor")
        from django.contrib.auth.models import User

        self._run({"Editor": ["newuser@example.com"]})
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_handle_skips_existing_users_with_usable_passwords(self):
        from django.contrib.auth.models import User

        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="password",
        )
        Group.objects.get_or_create(name="Editor")
        self._run({"Editor": ["existing@example.com"]})
        # Should not raise, just skip

    def test_handle_with_nonexistent_group(self):
        # Group doesn't exist — should handle gracefully
        self._run({"NonExistentGroup": ["user@example.com"]})
