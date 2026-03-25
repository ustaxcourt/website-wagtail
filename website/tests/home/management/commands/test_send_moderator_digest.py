import inspect
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

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


@override_settings(DEFAULT_FROM_EMAIL="")
def test_get_digest_from_email_falls_back_to_domain_name():
    assert (
        send_moderator_digest.get_digest_from_email("example.com")
        == "noreply@example.com"
    )


@override_settings()
def test_get_digest_from_email_returns_none_when_unset_and_no_domain():
    with patch.object(
        send_moderator_digest.settings, "DEFAULT_FROM_EMAIL", "", create=True
    ):
        assert send_moderator_digest.get_digest_from_email(None) is None


def test_send_moderator_digest_module_does_not_import_boto3():
    source = inspect.getsource(send_moderator_digest)

    assert "import boto3" not in source
    assert "boto3." not in source


def test_command_reports_message_and_recipient_counts_separately():
    fake_model = SimpleNamespace(objects=Mock())
    fake_group = SimpleNamespace(
        user_set=SimpleNamespace(
            all=lambda: [
                SimpleNamespace(
                    username="mod1",
                    first_name="Mod",
                    last_name="One",
                    email="mod1@example.com",
                ),
                SimpleNamespace(
                    username="mod2",
                    first_name="Mod",
                    last_name="Two",
                    email="mod2@example.com",
                ),
            ]
        )
    )
    fake_revision = SimpleNamespace(
        content_type=SimpleNamespace(model_class=lambda: fake_model),
        object_id="1",
        content={},
    )
    fake_object = SimpleNamespace(
        pk=1,
        title="Test item",
        revisions=SimpleNamespace(
            order_by=lambda *args, **kwargs: SimpleNamespace(
                first=lambda: fake_revision
            )
        ),
    )
    fake_model.objects.get.return_value = fake_object

    revision_qs = SimpleNamespace()
    revision_qs.select_related = lambda *args, **kwargs: revision_qs
    revision_qs.distinct = lambda: [fake_revision]

    comments_qs = SimpleNamespace(
        exclude=lambda *args, **kwargs: comments_qs,
        order_by=lambda *args, **kwargs: comments_qs,
        values_list=lambda *args, **kwargs: comments_qs,
        distinct=lambda: [],
    )
    recent_qs = SimpleNamespace(
        select_related=lambda *args, **kwargs: recent_qs,
        order_by=lambda *args, **kwargs: recent_qs,
        first=lambda: None,
    )

    stdout = StringIO()

    with (
        patch.object(
            send_moderator_digest.Group.objects, "get", return_value=fake_group
        ),
        patch.object(
            send_moderator_digest.Revision.objects, "filter", return_value=revision_qs
        ),
        patch.object(
            send_moderator_digest.TaskState.objects,
            "filter",
            side_effect=[comments_qs, recent_qs],
        ),
        patch.object(
            send_moderator_digest, "build_edit_url", return_value="/admin/edit/1"
        ),
        patch.object(
            send_moderator_digest.loader,
            "get_template",
            return_value=SimpleNamespace(render=lambda context: "<p>Digest</p>"),
        ),
        patch.object(send_moderator_digest, "send_digest_email", return_value=1),
    ):
        call_command("send_moderator_digest", stdout=stdout)

    output = stdout.getvalue()

    assert "Email backend reported 1 message(s) sent to 2 recipient(s)." in output


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
def test_command_exits_when_moderators_group_missing(capsys):
    call_command("send_moderator_digest")

    output = capsys.readouterr().out

    assert '"Moderators" group not found.' in output
