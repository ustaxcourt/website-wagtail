from unittest import mock

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from django.contrib.auth.models import AnonymousUser, User
from whitenoise.middleware import WhiteNoiseMiddleware

from app.middleware import (
    CachedWhiteNoiseMiddleware,
    CacheControlMiddleware,
    JSONExceptionMiddleware,
)


class TestJSONExceptionMiddleware:
    def setup_method(self):
        self.factory = RequestFactory()

    def _middleware(self, status_code=200):
        resp = HttpResponse(status=status_code)
        return JSONExceptionMiddleware(lambda r: resp), resp

    def test_200_passes_through(self):
        mw, expected = self._middleware(200)
        request = self.factory.get("/")
        response = mw(request)
        assert response.status_code == 200

    def test_404_returns_response(self):
        mw, _ = self._middleware(404)
        request = self.factory.get("/missing/")
        response = mw(request)
        assert response.status_code == 404

    def test_404_with_referer_and_user_agent(self):
        mw, _ = self._middleware(404)
        request = self.factory.get(
            "/missing/",
            HTTP_REFERER="http://example.com",
            HTTP_USER_AGENT="TestBot/1.0",
        )
        response = mw(request)
        assert response.status_code == 404

    def test_process_exception_returns_none(self):
        mw = JSONExceptionMiddleware(lambda r: HttpResponse())
        request = self.factory.get("/error/")
        result = mw.process_exception(request, RuntimeError("boom"))
        assert result is None

    def test_process_exception_with_remote_addr(self):
        mw = JSONExceptionMiddleware(lambda r: HttpResponse())
        request = self.factory.get("/error/", REMOTE_ADDR="1.2.3.4")
        result = mw.process_exception(request, ValueError("value error"))
        assert result is None


class TestCacheControlMiddleware:
    def setup_method(self):
        self.factory = RequestFactory()

    def _middleware(self):
        return CacheControlMiddleware(lambda r: HttpResponse())

    def test_login_path_sets_no_store(self):
        mw = self._middleware()
        request = self.factory.get("/login/")
        request.user = AnonymousUser()
        response = mw(request)
        assert "no-store" in response["Cache-Control"]

    def test_login_subpath_sets_no_store(self):
        mw = self._middleware()
        request = self.factory.get("/login/sso/")
        request.user = AnonymousUser()
        response = mw(request)
        assert "no-store" in response["Cache-Control"]

    def test_complete_path_sets_no_store(self):
        mw = self._middleware()
        request = self.factory.get("/complete/google/")
        request.user = AnonymousUser()
        response = mw(request)
        assert "no-store" in response["Cache-Control"]

    def test_login_sets_pragma_no_cache(self):
        mw = self._middleware()
        request = self.factory.get("/login/")
        request.user = AnonymousUser()
        response = mw(request)
        assert response["Pragma"] == "no-cache"

    def test_login_sets_expires_zero(self):
        mw = self._middleware()
        request = self.factory.get("/login/")
        request.user = AnonymousUser()
        response = mw(request)
        assert response["Expires"] == "0"

    def test_anonymous_user_gets_max_age(self):
        mw = self._middleware()
        request = self.factory.get("/about/")
        request.user = AnonymousUser()
        response = mw(request)
        assert response["Cache-Control"] == "max-age=300"

    @pytest.mark.django_db
    def test_authenticated_user_gets_private_no_cache(self):
        user = User.objects.create_user(username="authuser", password="pass")
        mw = self._middleware()
        request = self.factory.get("/dashboard/")
        request.user = user
        response = mw(request)
        assert "private" in response["Cache-Control"]
        assert "no-store" in response["Cache-Control"]

    @pytest.mark.django_db
    def test_authenticated_user_gets_logged_in_header(self):
        user = User.objects.create_user(username="loggedin", password="pass")
        mw = self._middleware()
        request = self.factory.get("/dashboard/")
        request.user = user
        response = mw(request)
        assert response["X-Logged-In-User"] == "true"

    @pytest.mark.django_db
    def test_authenticated_user_login_path_uses_no_store_not_private(self):
        """Login path takes priority over authenticated user rule."""
        user = User.objects.create_user(username="authlogin", password="pass")
        mw = self._middleware()
        request = self.factory.get("/login/redirect/")
        request.user = user
        response = mw(request)
        # login path rule fires first — should not have 'private'
        assert "private" not in response["Cache-Control"]
        assert "no-store" in response["Cache-Control"]


class TestCachedWhiteNoiseMiddleware:
    @pytest.fixture(autouse=True)
    def static_root(self, tmp_path):
        (tmp_path / "css").mkdir()
        (tmp_path / "css" / "site.css").write_text("body {}")
        CachedWhiteNoiseMiddleware._shared_state = None
        with override_settings(
            STATIC_ROOT=str(tmp_path),
            STATIC_URL="/static/",
            WHITENOISE_AUTOREFRESH=False,
        ):
            yield tmp_path
        CachedWhiteNoiseMiddleware._shared_state = None

    def setup_method(self):
        self.factory = RequestFactory()

    def test_static_root_is_scanned_only_once(self):
        """Wagtail preview re-instantiates middleware per render; only the first should walk STATIC_ROOT."""
        with mock.patch.object(
            WhiteNoiseMiddleware,
            "add_files",
            autospec=True,
            side_effect=WhiteNoiseMiddleware.add_files,
        ) as add_files:
            for _ in range(3):
                CachedWhiteNoiseMiddleware(lambda r: HttpResponse())
        assert add_files.call_count == 1

    def test_cached_instance_serves_static_files(self):
        CachedWhiteNoiseMiddleware(lambda r: HttpResponse())
        mw = CachedWhiteNoiseMiddleware(lambda r: HttpResponse(status=404))
        response = mw(self.factory.get("/static/css/site.css"))
        assert response.status_code == 200
        assert b"".join(response.streaming_content) == b"body {}"

    def test_each_instance_keeps_its_own_get_response(self):
        first = CachedWhiteNoiseMiddleware(lambda r: HttpResponse("first"))
        second = CachedWhiteNoiseMiddleware(lambda r: HttpResponse("second"))
        assert first(self.factory.get("/page/")).content == b"first"
        assert second(self.factory.get("/page/")).content == b"second"

    def test_autorefresh_mode_is_not_cached(self):
        with override_settings(WHITENOISE_AUTOREFRESH=True):
            CachedWhiteNoiseMiddleware(lambda r: HttpResponse())
        assert CachedWhiteNoiseMiddleware._shared_state is None
