"""Tests for home/management/commands/reset_admin_password.py"""

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
import home.management.commands.reset_admin_password as cmd_module


@pytest.mark.django_db
class TestResetAdminPasswordCommand:
    def test_updates_password_when_admin_exists(self):
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password="oldpassword"
        )
        original = cmd_module.DJANGO_SUPERUSER_PASSWORD
        cmd_module.DJANGO_SUPERUSER_PASSWORD = "newpass123"
        try:
            call_command("reset_admin_password")
        finally:
            cmd_module.DJANGO_SUPERUSER_PASSWORD = original

        user = User.objects.get(username="admin")
        assert user.check_password("newpass123")

    def test_prints_success_when_admin_exists(self, capsys):
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password="old"
        )
        original = cmd_module.DJANGO_SUPERUSER_PASSWORD
        cmd_module.DJANGO_SUPERUSER_PASSWORD = "testpass"
        try:
            call_command("reset_admin_password")
        finally:
            cmd_module.DJANGO_SUPERUSER_PASSWORD = original
        captured = capsys.readouterr()
        assert "successfully changed" in captured.out

    def test_prints_message_when_admin_does_not_exist(self, capsys):
        call_command("reset_admin_password")
        captured = capsys.readouterr()
        assert "does not exist" in captured.out
