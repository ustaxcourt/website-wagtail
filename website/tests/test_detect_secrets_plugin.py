import pytest

from detect_secrets_plugins.wagtail_transfer import WagtailTransferSecretKeyDetector


@pytest.fixture
def detector():
    return WagtailTransferSecretKeyDetector()


def _secrets(detector, line):
    return list(detector.analyze_string(line))


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
