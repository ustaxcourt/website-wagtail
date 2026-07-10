import io

import pytest

from detect_secrets_plugins.keywords import BroadKeywordDetector

FAKE_SECRET = "hardcoded-secret-value"  # pragma: allowlist secret
FAKE_SECRET_2 = "another-hardcoded-secret"  # pragma: allowlist secret


class _NamedIO(io.StringIO):
    """StringIO with a name attribute so analyze_file can reference the filename."""

    name = "<test>"


@pytest.fixture
def detector():
    return BroadKeywordDetector()


def _caught(detector, line):
    return list(detector.analyze_string(line))


def _caught_in_file(detector, content):
    return list(detector.analyze_file(_NamedIO(content)))


# --- Patterns that must be caught ---


def test_detects_standalone_key(detector):
    assert _caught(detector, f'KEY = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_standalone_token(detector):
    assert _caught(detector, f'TOKEN = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_standalone_auth(detector):
    assert _caught(detector, f'AUTH = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_standalone_credential(detector):
    assert _caught(detector, f'CREDENTIAL = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_compound_api_token(detector):
    assert _caught(detector, f'API_TOKEN = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_compound_access_token(detector):
    assert _caught(detector, f'ACCESS_TOKEN = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_compound_oauth_token(detector):
    assert _caught(detector, f'OAUTH_TOKEN = "{FAKE_SECRET}"') == [
        FAKE_SECRET
    ]  # pragma: allowlist secret


def test_detects_multiple_secrets_on_same_line(detector):
    line = (
        f'ACCESS_TOKEN = "{FAKE_SECRET}"; '  # pragma: allowlist secret
        f'REFRESH_TOKEN = "{FAKE_SECRET_2}"'  # pragma: allowlist secret
    )
    assert _caught(detector, line) == [
        FAKE_SECRET,
        FAKE_SECRET_2,
    ]  # pragma: allowlist secret


# --- Patterns that must NOT be caught ---


def test_ignores_env_var_lookup(detector):
    assert _caught(detector, 'TOKEN = os.getenv("TOKEN")') == []


def test_ignores_short_values(detector):
    assert _caught(detector, 'KEY = "short"') == []  # pragma: allowlist secret


def test_ignores_boolean_values(detector):
    assert _caught(detector, "AUTH = True") == []


def test_ignores_unrelated_variable_names(detector):
    assert (
        _caught(detector, f'MONKEY = "{FAKE_SECRET}"') == []
    )  # pragma: allowlist secret


def test_ignores_lowercase_key(detector):
    assert (
        _caught(detector, f'test_key = "{FAKE_SECRET}"') == []
    )  # pragma: allowlist secret


def test_ignores_lowercase_auth_token(detector):
    assert (
        _caught(detector, f'auth_token = "{FAKE_SECRET}"') == []
    )  # pragma: allowlist secret


def test_secret_type(detector):
    assert detector.secret_type == "Broad Secret Keyword"  # pragma: allowlist secret


# --- Multi-line detection ---


def test_detects_triple_quoted_multiline(detector):
    content = f'KEY = """\n{FAKE_SECRET}\n"""'  # pragma: allowlist secret
    results = _caught_in_file(detector, content)
    assert len(results) == 1
    assert results[0].secret_value == FAKE_SECRET  # pragma: allowlist secret
    assert results[0].type == detector.secret_type  # pragma: allowlist secret


def test_detects_parenthesized_multiline(detector):
    content = f'TOKEN = (\n    "{FAKE_SECRET}"\n)'  # pragma: allowlist secret
    results = _caught_in_file(detector, content)
    assert len(results) == 1
    assert results[0].secret_value == FAKE_SECRET  # pragma: allowlist secret


def test_no_duplicate_for_single_line(detector):
    content = f'KEY = "{FAKE_SECRET}"'  # pragma: allowlist secret
    results = _caught_in_file(detector, content)
    assert len(results) == 1
