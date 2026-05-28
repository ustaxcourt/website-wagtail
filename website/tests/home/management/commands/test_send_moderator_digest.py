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


@pytest.mark.django_db
@override_settings(DEFAULT_FROM_EMAIL="noreply@example.com")
def test_command_reports_message_and_recipient_counts_separately():
    from django.contrib.auth.models import Group, User

    moderators_group = Group.objects.create(name="Moderators")
    for i, (first, last, email) in enumerate(
        [
            ("Mod", "One", "mod1@example.com"),
            ("Mod", "Two", "mod2@example.com"),
        ]
    ):
        user = User.objects.create_user(
            username=f"mod{i}", first_name=first, last_name=last, email=email
        )
        user.groups.add(moderators_group)

    fake_model = SimpleNamespace(objects=Mock())
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

    assert (
        "Email backend reported 1 message(s) sent to 2 recipient(s)."
        in stdout.getvalue()
    )


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
def test_command_exits_when_moderators_group_missing(capsys):
    call_command("send_moderator_digest")

    output = capsys.readouterr().out

    assert '"Moderators" group not found.' in output


# ---- Additional tests for safe_parse_dt and build_edit_url ----


def test_safe_parse_dt_none_returns_none():
    assert send_moderator_digest.safe_parse_dt(None) is None


def test_safe_parse_dt_empty_string_returns_none():
    assert send_moderator_digest.safe_parse_dt("") is None


def test_safe_parse_dt_valid_iso_string():
    from django.utils import timezone

    result = send_moderator_digest.safe_parse_dt("2024-01-15T10:00:00")
    assert result is not None
    assert timezone.is_aware(result)


def test_safe_parse_dt_aware_datetime_returned():
    from django.utils import timezone

    aware_dt = timezone.now()
    result = send_moderator_digest.safe_parse_dt(aware_dt)
    assert result == aware_dt


def test_safe_parse_dt_naive_datetime_made_aware():
    from datetime import datetime
    from django.utils import timezone

    naive = datetime(2024, 3, 1, 12, 0, 0)
    result = send_moderator_digest.safe_parse_dt(naive)
    assert timezone.is_aware(result)


def test_safe_parse_dt_invalid_string_returns_none():
    result = send_moderator_digest.safe_parse_dt("not-a-date")
    assert result is None


def test_build_edit_url_returns_none_on_exception():
    with patch(
        "home.management.commands.send_moderator_digest.reverse",
        side_effect=Exception("error"),
    ):
        obj = Mock()
        result = send_moderator_digest.build_edit_url(obj, "example.com")
        assert result is None


@pytest.mark.django_db
def test_build_edit_url_for_page_with_domain():
    from wagtail.models import Page

    page = Mock(spec=Page)
    page.pk = 1
    with patch(
        "home.management.commands.send_moderator_digest.reverse",
        return_value="/admin/pages/1/edit/",
    ):
        result = send_moderator_digest.build_edit_url(page, "example.com")
        assert result == "https://example.com/admin/pages/1/edit/"


@pytest.mark.django_db
def test_build_edit_url_for_page_no_domain():
    from wagtail.models import Page

    page = Mock(spec=Page)
    page.pk = 1
    with patch(
        "home.management.commands.send_moderator_digest.reverse",
        return_value="/admin/pages/1/edit/",
    ):
        result = send_moderator_digest.build_edit_url(page, None)
        assert result == "/admin/pages/1/edit/"


def test_send_digest_email_with_no_recipients():
    count = send_moderator_digest.send_digest_email([], "<p>body</p>", "example.com")
    assert count == 0


def test_build_edit_url_fallback_to_kwargs_on_no_reverse_match():
    """Test NoReverseMatch fallback in build_edit_url for snippet."""
    from home.management.commands.send_moderator_digest import build_edit_url

    mock_obj = SimpleNamespace(pk=5)
    mock_ct = SimpleNamespace(app_label="home", model="newsitem")

    with (
        patch(
            "home.management.commands.send_moderator_digest.ContentType.objects.get_for_model",
            return_value=mock_ct,
        ),
        patch(
            "home.management.commands.send_moderator_digest.reverse",
            side_effect=[
                __import__("django.urls", fromlist=["NoReverseMatch"]).NoReverseMatch,
                "/admin/snippets/home/newsitem/5/edit/",
            ],
        ),
    ):
        result = build_edit_url(mock_obj, None)
        assert result == "/admin/snippets/home/newsitem/5/edit/"


def test_command_exits_when_no_recipient_emails():
    """Test command exits early when all users lack email addresses."""
    fake_group = SimpleNamespace(
        user_set=SimpleNamespace(
            all=lambda: [
                SimpleNamespace(
                    username="mod1",
                    first_name="Mod",
                    last_name="One",
                    email="",  # No email
                ),
            ]
        )
    )
    stdout = StringIO()

    with patch.object(
        send_moderator_digest.Group.objects, "get", return_value=fake_group
    ):
        call_command("send_moderator_digest", stdout=stdout)

    output = stdout.getvalue()
    assert "No recipient emails found" in output


def test_command_returns_when_no_items_in_moderation():
    """Test command exits early when no items are awaiting moderation."""
    fake_group = SimpleNamespace(
        user_set=SimpleNamespace(
            all=lambda: [
                SimpleNamespace(
                    username="mod1",
                    first_name="Mod",
                    last_name="One",
                    email="mod1@example.com",
                )
            ]
        )
    )

    revision_qs = SimpleNamespace()
    revision_qs.select_related = lambda *args, **kwargs: revision_qs
    revision_qs.distinct = lambda: []  # No revisions

    stdout = StringIO()

    with (
        patch.object(
            send_moderator_digest.Group.objects, "get", return_value=fake_group
        ),
        patch.object(
            send_moderator_digest.Revision.objects, "filter", return_value=revision_qs
        ),
    ):
        call_command("send_moderator_digest", stdout=stdout)

    output = stdout.getvalue()
    assert "No items are currently awaiting moderation" in output
