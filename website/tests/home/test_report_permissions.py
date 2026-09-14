"""Who can reach the admin report views."""

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

ADMIN_ONLY_REPORTS = [
    "news_and_announcements_report",
    "news_and_announcements_report_results",
    "search_definitions_report",
    "search_definitions_report_results",
]

EDITOR_VISIBLE_REPORTS = [
    "private_seminar_disclosure_report",
]


@pytest.fixture(autouse=True)
def renderable_admin(settings):
    """app.settings.test still spells the storage setting the pre-Django 5 way,
    so the manifest storage from base.py applies and rendering an admin page
    would need collected static files. GITHUB_SHA is only set in CI."""
    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
    settings.GITHUB_SHA = "0000000"


@pytest.fixture
def superuser(db):
    return User.objects.create_user(
        username="report-admin",
        email="report-admin@example.com",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def admin_access_user(db):
    """A non-superuser who can get into the Wagtail admin at all."""
    user = User.objects.create_user(
        username="report-editor",
        email="report-editor@example.com",
        password="testpass123",
        is_staff=True,
    )
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
    )
    return user


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ADMIN_ONLY_REPORTS + EDITOR_VISIBLE_REPORTS)
def test_superuser_can_open_every_report(client, superuser, url_name):
    client.force_login(superuser)
    assert client.get(reverse(url_name)).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ADMIN_ONLY_REPORTS)
def test_admin_only_reports_are_closed_to_other_admin_users(
    client, admin_access_user, url_name
):
    """These are registered with AdminOnlyMenuItem, so the view has to agree."""
    client.force_login(admin_access_user)
    assert client.get(reverse(url_name)).status_code != 200
    assert client.get(reverse(url_name), {"export": "csv"}).status_code != 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", EDITOR_VISIBLE_REPORTS)
def test_editor_visible_reports_stay_open(client, admin_access_user, url_name):
    client.force_login(admin_access_user)
    assert client.get(reverse(url_name)).status_code == 200
