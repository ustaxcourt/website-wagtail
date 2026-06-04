"""Tests for home/management/commands/preregister_superusers.py"""

import json
import pytest
from io import StringIO
from unittest.mock import patch, MagicMock

from home.management.commands.preregister_superusers import Command


class TestGetSuperusersFromSecret:
    def _make_cmd(self):
        cmd = Command.__new__(Command)
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        cmd.style = MagicMock()
        cmd.style.ERROR = lambda s: s
        cmd.style.SUCCESS = lambda s: s
        cmd.style.WARNING = lambda s: s
        return cmd

    def test_returns_list_when_secret_is_list(self):
        cmd = self._make_cmd()
        data = ["admin@example.com", "admin2@example.com"]
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            return_value=data,
        ):
            result = cmd.get_superusers_from_configured_secret()
        assert result == data

    def test_returns_list_when_secret_is_json_string(self):
        cmd = self._make_cmd()
        data = ["admin@example.com"]
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            return_value=json.dumps(data),
        ):
            result = cmd.get_superusers_from_configured_secret()
        assert result == data

    def test_returns_none_when_secret_is_none(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            return_value=None,
        ):
            result = cmd.get_superusers_from_configured_secret()
        assert result is None

    def test_returns_none_when_invalid_json(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            return_value="not json",
        ):
            result = cmd.get_superusers_from_configured_secret()
        assert result is None

    def test_returns_none_when_runtime_error(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            side_effect=RuntimeError("fail"),
        ):
            result = cmd.get_superusers_from_configured_secret()
        assert result is None

    def test_returns_none_when_unexpected_type(self):
        cmd = self._make_cmd()
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            return_value={"not": "list"},
        ):
            result = cmd.get_superusers_from_configured_secret()
        assert result is None


@pytest.mark.django_db
class TestPreregisterSuperusersHandle:
    def _run(self, secret_data):
        cmd = Command()
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        with patch(
            "home.management.commands.preregister_superusers.get_secret_from_aws",
            return_value=secret_data,
        ):
            cmd.handle()

    def test_handle_with_none_secret_does_not_crash(self):
        self._run(None)

    def test_handle_creates_superuser_from_email(self):
        from django.contrib.auth.models import User

        self._run(["newsuper@example.com"])
        assert User.objects.filter(
            email="newsuper@example.com", is_superuser=True
        ).exists()

    def test_handle_skips_existing_superuser(self):
        from django.contrib.auth.models import User

        User.objects.create_superuser(
            username="existing", email="existing@example.com", password="pw"
        )
        self._run(["existing@example.com"])
        # Should not raise or create duplicate
        assert User.objects.filter(email="existing@example.com").count() == 1
