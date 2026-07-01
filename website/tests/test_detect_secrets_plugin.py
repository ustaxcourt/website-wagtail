import io

import pytest

from detect_secrets_plugins.wagtail_transfer import WagtailTransferSecretKeyDetector


class _NamedIO(io.StringIO):
    """StringIO with a name attribute so analyze_file can reference the filename."""

    name = "<test>"


@pytest.fixture
def detector():
    return WagtailTransferSecretKeyDetector()


def _secrets(detector, line):
    return list(detector.analyze_string(line))


def _secrets_in_file(detector, content):
    return list(detector.analyze_file(_NamedIO(content)))


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


# --- Multi-line detection ---


def test_detects_triple_quoted_multiline(detector):
    content = 'WAGTAILTRANSFER_SECRET_KEY = """\nmy-super-secret-key\n"""'  # pragma: allowlist secret
    results = _secrets_in_file(detector, content)
    assert len(results) == 1
    assert results[0].secret_value == "my-super-secret-key"  # pragma: allowlist secret
    assert results[0].type == detector.secret_type  # pragma: allowlist secret


def test_no_duplicate_for_single_line(detector):
    content = (
        'WAGTAILTRANSFER_SECRET_KEY = "my-super-secret-key"'  # pragma: allowlist secret
    )
    results = _secrets_in_file(detector, content)
    assert len(results) == 1
