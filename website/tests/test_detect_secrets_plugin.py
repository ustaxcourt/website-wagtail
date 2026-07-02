from pathlib import Path

import pytest
from detect_secrets.core.plugins.util import get_mapping_from_secret_type_to_class
from detect_secrets.core.scan import scan_file
from detect_secrets.settings import transient_settings

from detect_secrets_plugins.wagtail_transfer import WagtailTransferSecretKeyDetector

_PLUGIN_FILE = (
    Path(__file__).resolve().parent.parent
    / "detect_secrets_plugins"
    / "wagtail_transfer.py"
)


@pytest.fixture
def detector():
    return WagtailTransferSecretKeyDetector()


def _secrets(detector, line):
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
                {
                    "name": "WagtailTransferSecretKeyDetector",
                    "path": f"file://{_PLUGIN_FILE}",
                }
            ]
        }
    ):
        return list(scan_file(str(target)))


def test_detects_double_quoted_secret(detector):
    line = (
        'WAGTAILTRANSFER_SECRET_KEY = "my-super-secret-key"'  # pragma: allowlist secret
    )
    assert _secrets(detector, line) == [
        "my-super-secret-key"
    ]  # pragma: allowlist secret


def test_detects_single_quoted_secret(detector):
    line = "WAGTAILTRANSFER_SECRET_KEY = 'another-secret-value'"  # pragma: allowlist secret
    assert _secrets(detector, line) == [
        "another-secret-value"
    ]  # pragma: allowlist secret


def test_detects_multiple_secrets_on_same_line(detector):
    line = (
        'WAGTAILTRANSFER_SECRET_KEY = "my-super-secret-key"; '  # pragma: allowlist secret
        'WAGTAILTRANSFER_SECRET_KEY = "another-secret-value"'  # pragma: allowlist secret
    )
    assert _secrets(detector, line) == [
        "my-super-secret-key",
        "another-secret-value",
    ]  # pragma: allowlist secret


def test_no_match_on_env_var_lookup(detector):
    line = 'WAGTAILTRANSFER_SECRET_KEY = os.getenv("WAGTAILTRANSFER_SECRET_KEY")'
    assert _secrets(detector, line) == []


def test_no_match_on_unrelated_line(detector):
    line = "DEBUG = True"
    assert _secrets(detector, line) == []


def test_no_match_on_short_value(detector):
    line = 'WAGTAILTRANSFER_SECRET_KEY = "short"'  # pragma: allowlist secret
    assert _secrets(detector, line) == []


def test_case_insensitive(detector):
    line = (
        'wagtailtransfer_secret_key = "my-super-secret-key"'  # pragma: allowlist secret
    )
    assert _secrets(detector, line) == [
        "my-super-secret-key"
    ]  # pragma: allowlist secret


def test_secret_type(detector):
    assert (
        detector.secret_type
        == "Wagtail Transfer Secret Key"  # pragma: allowlist secret
    )


# --- Multi-line detection, via the real detect-secrets pipeline ---
#
# detect-secrets' scan pipeline (`scan_file`/`scan_diff`) only ever calls a
# plugin's `analyze_line`, one physical line at a time. There is no "whole
# file" hook a plugin can implement, so multi-line detection has to work
# through the `context` (CodeSnippet) that `analyze_line` optionally
# receives - see WagtailTransferSecretKeyDetector.analyze_line. These tests
# go through `detect_secrets.core.scan.scan_file`, the same entry point
# `detect-secrets-hook` uses, rather than calling plugin internals directly,
# so they actually prove the secret is caught in a real scan/commit.


def test_detects_triple_quoted_multiline(tmp_path):
    content = 'WAGTAILTRANSFER_SECRET_KEY = """\nmy-super-secret-key\n"""\n'  # pragma: allowlist secret
    results = _scan(tmp_path, content)
    assert len(results) == 1
    assert results[0].secret_value == "my-super-secret-key"  # pragma: allowlist secret
    assert (
        results[0].type == WagtailTransferSecretKeyDetector.secret_type
    )  # pragma: allowlist secret


def test_no_duplicate_for_single_line(tmp_path):
    content = 'WAGTAILTRANSFER_SECRET_KEY = "my-super-secret-key"\n'  # pragma: allowlist secret
    results = _scan(tmp_path, content)
    assert len(results) == 1
