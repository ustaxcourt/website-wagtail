"""Tests for home/management/commands/production_checks.py"""

import pytest
from io import StringIO
from django.core.management import call_command
from django.test import override_settings
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestProductionChecksCommand:
    PASSING_SETTINGS = dict(
        DEBUG=False,
        SECRET_KEY="a-very-secret-key",
        ALLOWED_HOSTS=["example.com"],
        CSRF_COOKIE_SECURE=True,
        SESSION_COOKIE_SECURE=True,
    )

    def _make_superuser(self):
        return User.objects.create_superuser(
            username="admin", email="a@a.com", password="pw"
        )

    @override_settings(**PASSING_SETTINGS)
    def test_passes_with_valid_production_settings(self):
        self._make_superuser()
        out = StringIO()
        call_command("production_checks", stdout=out)
        assert "failed" not in out.getvalue().lower()

    @override_settings(**{**PASSING_SETTINGS, "DEBUG": True})
    def test_raises_when_debug_is_true(self):
        self._make_superuser()
        out = StringIO()
        with pytest.raises(RuntimeError, match="Production checks failed"):
            call_command("production_checks", stdout=out)
        assert "DEBUG" in out.getvalue()

    @override_settings(**{**PASSING_SETTINGS, "ALLOWED_HOSTS": []})
    def test_raises_when_allowed_hosts_empty(self):
        self._make_superuser()
        with pytest.raises(RuntimeError):
            call_command("production_checks", stdout=StringIO())

    @override_settings(**{**PASSING_SETTINGS, "CSRF_COOKIE_SECURE": False})
    def test_raises_when_csrf_not_secure(self):
        self._make_superuser()
        with pytest.raises(RuntimeError):
            call_command("production_checks", stdout=StringIO())

    @override_settings(**{**PASSING_SETTINGS, "SESSION_COOKIE_SECURE": False})
    def test_raises_when_session_not_secure(self):
        self._make_superuser()
        with pytest.raises(RuntimeError):
            call_command("production_checks", stdout=StringIO())

    @override_settings(**PASSING_SETTINGS)
    def test_raises_when_no_superuser(self):
        # Don't create a superuser
        with pytest.raises(RuntimeError):
            call_command("production_checks", stdout=StringIO())

    @override_settings(**PASSING_SETTINGS)
    def test_raises_when_non_superuser_has_password(self):
        self._make_superuser()
        User.objects.create_user(username="regular", password="pw", is_superuser=False)
        with pytest.raises(RuntimeError):
            call_command("production_checks", stdout=StringIO())
