"""Tests for app/wagtaillinkchecker/scanner.py"""

from unittest.mock import patch, MagicMock
import requests as requests_lib
from app.wagtaillinkchecker.scanner import Link, get_url, clean_url


def _make_mock_site(root_url="https://example.com"):
    site = MagicMock()
    site.root_url = root_url
    return site


def _make_response(status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    return resp


# ---------------------------------------------------------------------------
# Link class
# ---------------------------------------------------------------------------


class TestLinkMessage:
    def test_error_attribute_is_returned_directly(self):
        """When Link.error is set, Link.message returns it verbatim without inspecting status_code."""

        link = Link(url="https://example.com", page=None, error="Custom error message")
        assert link.message == "Custom error message"

    def test_success_message_for_2xx_status_code(self):
        link = Link(url="https://example.com", page=None, status_code=200)
        assert link.message == "Success"

    def test_success_message_for_1xx_status_code(self):
        link = Link(url="https://example.com", page=None, status_code=100)
        assert link.message == "Success"

    def test_5xx_on_own_site_url_returns_admin_notification_message(self):
        """5xx responses for internal (same-site) URLs produce a friendlier admin-oriented message."""

        site = _make_mock_site("https://example.com")
        link = Link(
            url="https://example.com/internal-page",
            page=None,
            status_code=500,
            site=site,
        )
        assert "500" in link.message
        assert "Internal server error" in link.message

    def test_5xx_on_external_url_returns_standard_http_message(self):
        """5xx responses for external URLs fall through to the standard http.client response text."""

        site = _make_mock_site("https://example.com")
        link = Link(
            url="https://external.com/page",
            page=None,
            status_code=500,
            site=site,
        )
        assert "500" in link.message
        assert "Internal Server Error" in link.message

    def test_known_4xx_status_code_returns_http_standard_message(self):
        link = Link(url="https://example.com", page=None, status_code=404)
        assert "404" in link.message
        assert "Not Found" in link.message

    def test_unrecognized_status_code_returns_unknown_error_message(self):
        link = Link(url="https://example.com", page=None, status_code=999)
        assert "999" in link.message
        assert "Unknown error" in link.message


class TestLinkIdentity:
    def test_str_returns_url(self):
        link = Link(url="https://example.com", page=None)
        assert str(link) == "https://example.com"

    def test_links_with_same_url_are_equal(self):
        a = Link(url="https://example.com", page=None)
        b = Link(url="https://example.com", page=None)
        assert a == b

    def test_links_with_different_urls_are_not_equal(self):
        a = Link(url="https://example.com", page=None)
        b = Link(url="https://other.com", page=None)
        assert a != b

    def test_hash_is_derived_from_url(self):
        link = Link(url="https://example.com", page=None)
        assert hash(link) == hash("https://example.com")

    def test_equality_with_non_link_returns_not_implemented(self):
        link = Link(url="https://example.com", page=None)
        assert link.__eq__("not a link") is NotImplemented


# ---------------------------------------------------------------------------
# get_url()
# ---------------------------------------------------------------------------


class TestGetUrl:
    def test_successful_get_request_returns_response(self):
        site = _make_mock_site()
        mock_resp = _make_response(200)
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get", return_value=mock_resp
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is False
        assert result["response"] is mock_resp

    def test_successful_head_request_returns_response(self):
        site = _make_mock_site()
        mock_resp = _make_response(200)
        with patch(
            "app.wagtaillinkchecker.scanner.requests.head", return_value=mock_resp
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=False
            )
        assert result["error"] is False
        assert result["response"] is mock_resp

    def test_head_falls_back_to_get_on_4xx_response(self):
        """A 4xx HEAD response retries with a full GET to avoid false positives from servers that block HEAD."""

        site = _make_mock_site()
        with (
            patch(
                "app.wagtaillinkchecker.scanner.requests.head",
                return_value=_make_response(404),
            ),
            patch(
                "app.wagtaillinkchecker.scanner.requests.get",
                return_value=_make_response(200),
            ),
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=False
            )
        assert result["error"] is False

    def test_get_sets_error_with_known_message_for_4xx(self):
        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            return_value=_make_response(404),
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is True
        assert result["status_code"] == 404
        assert "Not Found" in result["error_message"]

    def test_get_sets_client_error_message_for_unmapped_4xx(self):
        """A 4xx code absent from HTTP_STATUS_CODES falls back to a generic 'Client error' message."""

        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            return_value=_make_response(490),  # not in HTTP_STATUS_CODES
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is True
        assert result["error_message"] == "Client error"

    def test_get_sets_server_error_message_for_unmapped_5xx(self):
        """A 5xx code absent from HTTP_STATUS_CODES falls back to a generic 'Server Error' message."""

        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            return_value=_make_response(520),  # not in HTTP_STATUS_CODES
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is True
        assert result["error_message"] == "Server Error"

    def test_get_sets_unknown_status_message_for_out_of_range_code(self):
        """A status code outside 400-599 (e.g. 600) uses the 'Unknown HTTP Status Code' fallback."""

        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            return_value=_make_response(600),
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is True
        assert "600" in result["error_message"]

    def test_head_falls_back_to_get_on_connection_error(self):
        """A ConnectionError on HEAD retries with a full GET before reporting failure."""
        # From Claude: ConnectionError is raised when the TCP connection can't be established
        # (DNS failure, host unreachable, connection refused). These conditions apply at the
        # OS network layer — they affect both HEAD and GET for the same host at the same instant.
        # Mocking HEAD to fail with ConnectionError and GET to immediately return 200 is a
        # scenario that can't occur in production.

        site = _make_mock_site()
        with (
            patch(
                "app.wagtaillinkchecker.scanner.requests.head",
                side_effect=requests_lib.exceptions.ConnectionError,
            ),
            patch(
                "app.wagtaillinkchecker.scanner.requests.get",
                return_value=_make_response(200),
            ),
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=False
            )
        assert result["error"] is False

    def test_head_falls_back_to_get_on_connection_error_that_also_errors(self):
        """A ConnectionError on HEAD retries with a full GET before reporting failure."""
        # From Claude: ConnectionError is raised when the TCP connection can't be established
        # (DNS failure, host unreachable, connection refused). These conditions apply at the
        # OS network layer — they affect both HEAD and GET for the same host at the same instant.

        # Mocking HEAD to fail with ConnectionError and GET to also fail with ConnectionError
        # is a scenario that can occur in production.

        site = _make_mock_site()
        with (
            patch(
                "app.wagtaillinkchecker.scanner.requests.head",
                side_effect=requests_lib.exceptions.ConnectionError,
            ),
            patch(
                "app.wagtaillinkchecker.scanner.requests.get",
                side_effect=requests_lib.exceptions.ConnectionError,
            ),
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=False
            )
        assert result["error"] is True
        assert "connecting" in str(result["error_message"])

    def test_get_sets_error_on_connection_error(self):
        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            side_effect=requests_lib.exceptions.ConnectionError,
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is True
        assert "connecting" in str(result["error_message"])

    def test_head_falls_back_to_get_on_invalid_schema(self):
        """An InvalidSchema on HEAD retries with GET, which may succeed for schemas requests can handle."""

        site = _make_mock_site()
        with (
            patch(
                "app.wagtaillinkchecker.scanner.requests.head",
                side_effect=requests_lib.exceptions.InvalidSchema,
            ),
            patch(
                "app.wagtaillinkchecker.scanner.requests.get",
                return_value=_make_response(200),
            ),
        ):
            result = get_url(
                "tel://123-456-7890", page=None, site=site, get_full_result=False
            )
        assert result["invalid_schema"] is False
        assert result["error"] is False

    def test_get_sets_invalid_schema_flag_on_invalid_schema(self):
        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            side_effect=requests_lib.exceptions.InvalidSchema,
        ):
            result = get_url(
                "tel://123-456-7890", page=None, site=site, get_full_result=True
            )
        assert result["invalid_schema"] is True
        assert result["error"] is False

    def test_get_sets_error_on_generic_request_exception(self):
        """A RequestException that is not ConnectionError or InvalidSchema sets error=True."""

        site = _make_mock_site()
        with patch(
            "app.wagtaillinkchecker.scanner.requests.get",
            side_effect=requests_lib.exceptions.Timeout,
        ):
            result = get_url(
                "https://example.com", page=None, site=site, get_full_result=True
            )
        assert result["error"] is True
        assert "Timeout" in result["error_message"]
        assert result["status_code"] is None


# ---------------------------------------------------------------------------
# clean_url()
# ---------------------------------------------------------------------------


class TestCleanUrl:
    def test_relative_url_is_prefixed_with_site_root_url(self):
        site = _make_mock_site("https://example.com")
        assert clean_url("/about", site) == "https://example.com/about"

    def test_absolute_url_is_returned_unchanged(self):
        site = _make_mock_site("https://example.com")
        assert clean_url("https://other.com/page", site) == "https://other.com/page"

    def test_hash_anchor_returns_none(self):
        assert clean_url("#", _make_mock_site()) is None

    def test_none_input_returns_none(self):
        assert clean_url(None, _make_mock_site()) is None

    def test_empty_string_returns_none(self):
        assert clean_url("", _make_mock_site()) is None
