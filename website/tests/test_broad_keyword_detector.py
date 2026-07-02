from pathlib import Path

import pytest
from detect_secrets.core.plugins.util import get_mapping_from_secret_type_to_class
from detect_secrets.core.scan import scan_file
from detect_secrets.settings import transient_settings

from detect_secrets_plugins.keywords import BroadKeywordDetector

FAKE_SECRET = "hardcoded-secret-value"  # pragma: allowlist secret
FAKE_SECRET_2 = "another-hardcoded-secret"  # pragma: allowlist secret

_PLUGIN_FILE = (
    Path(__file__).resolve().parent.parent / "detect_secrets_plugins" / "keywords.py"
)


@pytest.fixture
def detector():
    return BroadKeywordDetector()


def _caught(detector, line):
    return list(detector.analyze_string(line))


def _scan(tmp_path, content):
    """Scan `content` through the real detect-secrets pipeline (scan_file),
    the same entry point `detect-secrets-hook` uses - not just the plugin's
    own analyze_string/analyze_line in isolation."""
    target = tmp_path / "settings.py"
    target.write_text(content)

    # detect-secrets caches the custom-plugin class mapping (keyed by
    # module contents, not by config) across `transient_settings` calls, so
    # a different test file configuring a different custom plugin earlier
    # in the run can leave a stale mapping. Not an issue for the real
    # pre-commit hook (single process, all plugins loaded together once).
    get_mapping_from_secret_type_to_class.cache_clear()

    with transient_settings(
        {
            "plugins_used": [
                {"name": "BroadKeywordDetector", "path": f"file://{_PLUGIN_FILE}"}
            ]
        }
    ):
        return list(scan_file(str(target)))


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


# --- Multi-line detection, via the real detect-secrets pipeline ---
#
# detect-secrets' scan pipeline (`scan_file`/`scan_diff`) only ever calls a
# plugin's `analyze_line`, one physical line at a time. There is no "whole
# file" hook a plugin can implement, so multi-line detection has to work
# through the `context` (CodeSnippet) that `analyze_line` optionally
# receives - see BroadKeywordDetector.analyze_line. These tests go through
# `detect_secrets.core.scan.scan_file`, the same entry point
# `detect-secrets-hook` uses, rather than calling plugin internals directly,
# so they actually prove secrets are caught in a real scan/commit.


def test_detects_triple_quoted_multiline(tmp_path):
    content = f'KEY = """\n{FAKE_SECRET}\n"""\n'  # pragma: allowlist secret
    results = _scan(tmp_path, content)
    assert len(results) == 1
    assert results[0].secret_value == FAKE_SECRET  # pragma: allowlist secret
    assert (
        results[0].type == BroadKeywordDetector.secret_type
    )  # pragma: allowlist secret


def test_detects_parenthesized_multiline(tmp_path):
    content = f'TOKEN = (\n    "{FAKE_SECRET}"\n)\n'  # pragma: allowlist secret
    results = _scan(tmp_path, content)
    assert len(results) == 1
    assert results[0].secret_value == FAKE_SECRET  # pragma: allowlist secret


def test_no_duplicate_for_single_line(tmp_path):
    content = f'KEY = "{FAKE_SECRET}"\n'  # pragma: allowlist secret
    results = _scan(tmp_path, content)
    assert len(results) == 1


def test_no_duplicate_across_overlapping_context_windows(tmp_path):
    # Two multi-line secrets close enough together to fall in each other's
    # context window - each must be reported exactly once, not once per
    # line it overlaps with.
    content = (
        f'KEY = """\n{FAKE_SECRET}\n"""\n'  # pragma: allowlist secret
        f'TOKEN = (\n    "{FAKE_SECRET_2}"\n)\n'  # pragma: allowlist secret
    )
    results = _scan(tmp_path, content)
    secret_values = {r.secret_value for r in results}
    assert secret_values == {FAKE_SECRET, FAKE_SECRET_2}  # pragma: allowlist secret
    assert len(results) == 2
