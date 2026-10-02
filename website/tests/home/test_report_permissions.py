"""Tests for access control and permissions on Wagtail admin report views and menu items."""

import pytest
from django.contrib.auth.models import Group, Permission, User
from django.test import RequestFactory
from django.urls import reverse

from home.views import NewsItemReportView, SearchDefinitionsReportView
from home.wagtail_hooks import PermissionCheckedMenuItem

RESTRICTED_REPORTS = [
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
    """Ensure staticfiles storage and GITHUB_SHA are configured for test environment."""
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
        password="testpass123",  # pragma: allowlist secret
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def admin_group_user(db):
    """A user in the Administrators group with report permissions and admin access."""
    user = User.objects.create_user(
        username="report-administrator",
        email="report-administrator@example.com",
        password="testpass123",  # pragma: allowlist secret
        is_staff=True,
    )
    admin_perm = Permission.objects.get(
        content_type__app_label="wagtailadmin", codename="access_admin"
    )
    user.user_permissions.add(admin_perm)

    group, _ = Group.objects.get_or_create(name="Administrators")
    news_perm = Permission.objects.get(
        codename="view_newsitem", content_type__app_label="home"
    )
    def_perm = Permission.objects.get(
        codename="view_definitionsquery", content_type__app_label="search"
    )
    group.permissions.add(news_perm, def_perm)
    user.groups.add(group)
    return user


@pytest.fixture
def moderator_user(db):
    """A user in the Moderators group with report permissions and admin access."""
    user = User.objects.create_user(
        username="report-moderator",
        email="report-moderator@example.com",
        password="testpass123",  # pragma: allowlist secret
        is_staff=True,
    )
    admin_perm = Permission.objects.get(
        content_type__app_label="wagtailadmin", codename="access_admin"
    )
    user.user_permissions.add(admin_perm)

    group, _ = Group.objects.get_or_create(name="Moderators")
    news_perm = Permission.objects.get(
        codename="view_newsitem", content_type__app_label="home"
    )
    def_perm = Permission.objects.get(
        codename="view_definitionsquery", content_type__app_label="search"
    )
    group.permissions.add(news_perm, def_perm)
    user.groups.add(group)
    return user


@pytest.fixture
def editor_user(db):
    """An editor with report permissions and admin access."""
    user = User.objects.create_user(
        username="report-editor",
        email="report-editor@example.com",
        password="testpass123",  # pragma: allowlist secret
        is_staff=True,
    )
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
    )
    group, _ = Group.objects.get_or_create(name="Editors")
    news_perm = Permission.objects.get(
        codename="view_newsitem", content_type__app_label="home"
    )
    def_perm = Permission.objects.get(
        codename="view_definitionsquery", content_type__app_label="search"
    )
    group.permissions.add(news_perm, def_perm)
    user.groups.add(group)
    return user


@pytest.fixture
def unauthorized_admin_user(db):
    """A user who has admin access but does NOT have view permissions for the report models."""
    user = User.objects.create_user(
        username="report-unauthorized",
        email="report-unauthorized@example.com",
        password="testpass123",  # pragma: allowlist secret
        is_staff=True,
    )
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
    )
    return user


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", RESTRICTED_REPORTS + EDITOR_VISIBLE_REPORTS)
def test_superuser_can_open_every_report(client, superuser, url_name):
    client.force_login(superuser)
    assert client.get(reverse(url_name)).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", RESTRICTED_REPORTS)
def test_superuser_can_export_reports(client, superuser, url_name):
    client.force_login(superuser)
    assert client.get(reverse(url_name), {"export": "csv"}).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", RESTRICTED_REPORTS + EDITOR_VISIBLE_REPORTS)
def test_administrators_group_user_can_access_reports(
    client, admin_group_user, url_name
):
    client.force_login(admin_group_user)
    assert client.get(reverse(url_name)).status_code == 200
    assert client.get(reverse(url_name), {"export": "csv"}).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", RESTRICTED_REPORTS + EDITOR_VISIBLE_REPORTS)
def test_moderators_group_user_can_access_reports(client, moderator_user, url_name):
    client.force_login(moderator_user)
    assert client.get(reverse(url_name)).status_code == 200
    assert client.get(reverse(url_name), {"export": "csv"}).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", RESTRICTED_REPORTS + EDITOR_VISIBLE_REPORTS)
def test_editors_group_user_can_access_reports(client, editor_user, url_name):
    client.force_login(editor_user)
    assert client.get(reverse(url_name)).status_code == 200
    assert client.get(reverse(url_name), {"export": "csv"}).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", RESTRICTED_REPORTS)
def test_unauthorized_user_cannot_access_restricted_reports(
    client, unauthorized_admin_user, url_name
):
    """Users without view permissions are redirected to admin home with permission denied."""
    client.force_login(unauthorized_admin_user)
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert response.url == reverse("wagtailadmin_home")

    csv_response = client.get(reverse(url_name), {"export": "csv"})
    assert csv_response.status_code == 302
    assert csv_response.url == reverse("wagtailadmin_home")


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", EDITOR_VISIBLE_REPORTS)
def test_unauthorized_user_can_access_open_reports(
    client, unauthorized_admin_user, url_name
):
    """The private seminar disclosure report remains accessible to any admin user."""
    client.force_login(unauthorized_admin_user)
    assert client.get(reverse(url_name)).status_code == 200


@pytest.mark.django_db
def test_permission_checked_menu_item_visibility(
    superuser, admin_group_user, moderator_user, editor_user, unauthorized_admin_user
):
    """Menu items are shown to authorized users and hidden from unauthorized users."""
    factory = RequestFactory()

    news_menu_item = PermissionCheckedMenuItem(
        "News Report",
        reverse("news_and_announcements_report"),
        permission_policy=NewsItemReportView.permission_policy,
        permission_required=NewsItemReportView.permission_required,
    )
    def_menu_item = PermissionCheckedMenuItem(
        "Definitions Report",
        reverse("search_definitions_report"),
        permission_policy=SearchDefinitionsReportView.permission_policy,
        permission_required=SearchDefinitionsReportView.permission_required,
    )

    for user, expected in [
        (superuser, True),
        (admin_group_user, True),
        (moderator_user, True),
        (editor_user, True),
        (unauthorized_admin_user, False),
    ]:
        req = factory.get("/admin/")
        req.user = user
        assert news_menu_item.is_shown(req) is expected, (
            f"news item visibility failed for {user.username}"
        )
        assert def_menu_item.is_shown(req) is expected, (
            f"def item visibility failed for {user.username}"
        )
