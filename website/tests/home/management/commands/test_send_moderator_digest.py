import inspect
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.test import override_settings

from home.management.commands import send_moderator_digest


@override_settings(DEFAULT_FROM_EMAIL="noreply@example.com")
def test_send_digest_email_uses_django_send_mail():
    recipient_emails = ["moderator@example.com"]
    email_html = "<p>Digest body</p>"

    with patch(
        "home.management.commands.send_moderator_digest.send_mail",
        return_value=1,
    ) as mock_send_mail:
        sent_count = send_moderator_digest.send_digest_email(
            recipient_emails, email_html, "example.com"
        )

    assert sent_count == 1
    mock_send_mail.assert_called_once_with(
        subject="Wagtail Daily Moderator Digest",
        message="Digest body",
        from_email="noreply@example.com",
        recipient_list=recipient_emails,
        html_message=email_html,
    )


def test_send_moderator_digest_module_does_not_import_boto3():
    source = inspect.getsource(send_moderator_digest)

    assert "import boto3" not in source
    assert "boto3." not in source


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
def test_command_exits_when_moderators_group_missing(capsys):
    call_command("send_moderator_digest")

    output = capsys.readouterr().out

    assert '"Moderators" group not found.' in output
