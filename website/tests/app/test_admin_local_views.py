"""Tests for app/admin_local/views.py"""

import pytest
from django.test import RequestFactory, override_settings
from django.http import Http404
from django.contrib.auth.models import AnonymousUser

from app.admin_local.views import LocalLoginView


class TestLocalLoginView:
    def _get_response(self, enable=True):
        factory = RequestFactory()
        request = factory.get("/admin/local-login/")
        request.user = AnonymousUser()
        request.session = {}
        view = LocalLoginView.as_view()
        return view(request)

    @override_settings(ENABLE_LOCAL_LOGIN=False)
    def test_raises_404_when_disabled(self):
        factory = RequestFactory()
        request = factory.get("/admin/local-login/")
        request.user = AnonymousUser()
        # Must attach a session for middleware
        from django.contrib.sessions.backends.cache import SessionStore

        request.session = SessionStore()
        view = LocalLoginView.as_view()
        with pytest.raises(Http404):
            view(request)

    @override_settings(ENABLE_LOCAL_LOGIN=True, WAGTAIL_CONTENT_LANGUAGES=[])
    def test_sets_x_robots_tag_header(self):
        factory = RequestFactory()
        request = factory.get("/admin/local-login/")
        request.user = AnonymousUser()
        from django.contrib.sessions.backends.cache import SessionStore

        request.session = SessionStore()
        view = LocalLoginView.as_view()
        response = view(request)
        assert response.get("X-Robots-Tag") == "noindex, nofollow, noarchive"

    @override_settings(ENABLE_LOCAL_LOGIN=True)
    def test_sets_cache_control_no_store(self):
        factory = RequestFactory()
        request = factory.get("/admin/local-login/")
        request.user = AnonymousUser()
        from django.contrib.sessions.backends.cache import SessionStore

        request.session = SessionStore()
        view = LocalLoginView.as_view()
        response = view(request)
        assert "no-store" in response.get("Cache-Control", "")
