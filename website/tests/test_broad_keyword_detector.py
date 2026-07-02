import io
from pathlib import Path

import pytest
from detect_secrets.core.scan import scan_file
from detect_secrets.settings import transient_settings

from detect_secrets_plugins.keywords import BroadKeywordDetector

FAKE_SECRET = "hardcoded-secret-value"  # pragma: allowlist secret
FAKE_SECRET_2 = "another-hardcoded-secret"  # pragma: allowlist secret

_PLUGIN_FILE = (
    Path(__file__).resolve().parent.parent / "detect_secrets_plugins" / "keywords.py"
)


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


# --- Real pipeline (what pre-commit / CI actually invoke) ---
#
# detect-secrets' scan pipeline (`scan_file`/`scan_diff`) only ever calls a
# plugin's `analyze_line`/`analyze_string`; it never calls `analyze_file`.
# `_caught_in_file` above calls `analyze_file` directly, so it doesn't prove
# the multi-line detection actually runs during a real scan. These tests
# go through `detect_secrets.core.scan.scan_file`, the same entry point
# `detect-secrets-hook` uses, to check that.


def test_triple_quoted_multiline_secret_caught_by_real_scan(tmp_path):
    target = tmp_path / "settings.py"
    target.write_text(f'KEY = """\n{FAKE_SECRET}\n"""\n')  # pragma: allowlist secret

    with transient_settings(
        {
            "plugins_used": [
                {"name": "BroadKeywordDetector", "path": f"file://{_PLUGIN_FILE}"}
            ]
        }
    ):
        results = list(scan_file(str(target)))

    assert results, (
        "BroadKeywordDetector.analyze_file() detects triple-quoted multi-line secrets, "
        "but detect-secrets never calls analyze_file() during a real scan — only "
        "analyze_line()/analyze_string(). This secret is silently missed by "
        "`detect-secrets-hook` (the command pre-commit/CI actually run)."
    )


def test_parenthesized_multiline_secret_caught_by_real_scan(tmp_path):
    target = tmp_path / "settings.py"
    target.write_text(
        f'TOKEN = (\n    "{FAKE_SECRET}"\n)\n'
    )  # pragma: allowlist secret

    with transient_settings(
        {
            "plugins_used": [
                {"name": "BroadKeywordDetector", "path": f"file://{_PLUGIN_FILE}"}
            ]
        }
    ):
        results = list(scan_file(str(target)))

    assert results, (
        "BroadKeywordDetector.analyze_file() detects parenthesized multi-line secrets, "
        "but detect-secrets never calls analyze_file() during a real scan — only "
        "analyze_line()/analyze_string(). This secret is silently missed by "
        "`detect-secrets-hook` (the command pre-commit/CI actually run)."
    )
