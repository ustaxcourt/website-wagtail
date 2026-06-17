"""Tests for app/role_switcher/views.py"""

import pytest
from unittest.mock import MagicMock
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages.storage.fallback import FallbackStorage

User = get_user_model()


def _add_messages(request):
    """Attach message storage to a request."""
    setattr(request, "_messages", FallbackStorage(request))
    return request


@pytest.mark.django_db
class TestSwitchRoleViewAssumeRole:
    def test_post_assume_role_by_non_superuser_redirects(self):
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_user(username="regular", password="pass")
        group = Group.objects.create(name="Editors")
        factory = RequestFactory()
        request = factory.post(
            "/switch-role/", {"assume_role": "1", "role": str(group.pk)}
        )
        request.user = user
        request.session = {}
        _add_messages(request)
        response = switch_role_view(request)
        assert response.status_code == 302
        assert "switch_role" in response["Location"] or response["Location"].endswith(
            "/switch-role/"
        )

    def test_post_assume_role_by_superuser_already_assuming_redirects(self):
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_superuser(
            username="admin2", password="pass", email="b@b.com"
        )
        group = Group.objects.create(name="Editors2")
        factory = RequestFactory()
        request = factory.post(
            "/switch-role/", {"assume_role": "1", "role": str(group.pk)}
        )
        request.user = user
        request.session = {"is_assuming_role": True}
        _add_messages(request)
        response = switch_role_view(request)
        assert response.status_code == 302

    def test_post_assume_role_valid_switches_role(self):
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_superuser(
            username="admin3", password="pass", email="c@c.com"
        )
        group = Group.objects.create(name="Editors3")
        factory = RequestFactory()
        request = factory.post(
            "/switch-role/", {"assume_role": "1", "role": str(group.pk)}
        )
        request.user = user
        request.session = {}
        _add_messages(request)
        response = switch_role_view(request)
        assert response.status_code == 302
        # User should no longer be superuser
        user.refresh_from_db()
        assert not user.is_superuser


@pytest.mark.django_db
class TestSwitchRoleViewRevertRole:
    def test_post_revert_role_when_not_assuming_redirects(self):
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_superuser(
            username="admin4", password="pass", email="d@d.com"
        )
        factory = RequestFactory()
        request = factory.post("/switch-role/", {"revert_role": "1"})
        request.user = user
        request.session = {"is_assuming_role": False}
        _add_messages(request)
        response = switch_role_view(request)
        assert response.status_code == 302

    def test_post_revert_role_restores_superuser(self):
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_user(username="admin5", password="pass")
        user.is_staff = True
        user.save()
        factory = RequestFactory()
        request = factory.post("/switch-role/", {"revert_role": "1"})
        request.user = user
        request.session = {
            "is_assuming_role": True,
            "original_is_superuser": True,
            "original_is_staff": True,
            "original_groups_pks": [],
            "assumed_role_name": "Editors",
        }
        _add_messages(request)
        response = switch_role_view(request)
        assert response.status_code == 302
        # User restored to superuser
        user.refresh_from_db()
        assert user.is_superuser

    def test_post_revert_role_restores_original_groups(self):
        """Covers lines 92-93: restoring non-empty original_groups_pks."""
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_user(username="admin6", password="pass")
        user.is_staff = True
        user.save()
        group = Group.objects.create(name="OriginalGroup")
        factory = RequestFactory()
        request = factory.post("/switch-role/", {"revert_role": "1"})
        request.user = user
        request.session = {
            "is_assuming_role": True,
            "original_is_superuser": True,
            "original_is_staff": True,
            "original_groups_pks": [group.pk],
            "assumed_role_name": "Editors",
        }
        _add_messages(request)
        response = switch_role_view(request)
        assert response.status_code == 302
        user.refresh_from_db()
        assert group in user.groups.all()


@pytest.mark.django_db
class TestSwitchRoleViewGET:
    def test_get_request_non_superuser_shows_no_form(self):
        from app.role_switcher.views import switch_role_view

        user = User.objects.create_user(username="nonadmin_get", password="pass")
        factory = RequestFactory()
        request = factory.get("/switch-role/")
        request.user = user
        request.session = {}
        _add_messages(request)
        from unittest.mock import patch

        with patch("app.role_switcher.views.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            switch_role_view(request)
            ctx = mock_render.call_args[0][2]
            assert ctx["can_initiate_new_switch"] is False
            assert ctx["role_switch_form"] is None

    def test_get_request_superuser_shows_form(self):
        from app.role_switcher.views import switch_role_view
        from unittest.mock import MagicMock, patch

        user = User.objects.create_superuser(
            username="admin_get2", password="pass", email="x@x.com"
        )
        factory = RequestFactory()
        request = factory.get("/switch-role/")
        request.user = user
        request.session = {}
        _add_messages(request)

        with patch("app.role_switcher.views.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            switch_role_view(request)
            ctx = mock_render.call_args[0][2]
            assert ctx["can_initiate_new_switch"] is True
            assert ctx["role_switch_form"] is not None

    def test_post_assume_role_with_invalid_form_passes_form_to_context(self):
        """Covers line 64: form_to_pass_in_context = form (invalid form case)."""
        from app.role_switcher.views import switch_role_view
        from unittest.mock import MagicMock, patch

        user = User.objects.create_superuser(
            username="admin_invalid", password="pass", email="inv@inv.com"
        )
        factory = RequestFactory()
        request = factory.post("/switch-role/", {"assume_role": "1", "role": "99999"})
        request.user = user
        request.session = {}
        _add_messages(request)

        with patch("app.role_switcher.views.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            switch_role_view(request)
            ctx = mock_render.call_args[0][2]
            assert ctx["role_switch_form"] is not None
