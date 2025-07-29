import os
import sys
import re
import django
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

REDIRECT_PATTERN = re.compile(
    r"^/documents/Rule-\d+[.\-_A-Za-z0-9]*?"
    r"(amended|Amended|superseded|2nd|2nd-amended|New|new)[^/]*\.pdf$"
)

STRIP_PATTERN = re.compile(r"^/documents/(Rule-\d+(?:\.\d+)?)[\w.\-]*\.pdf$")
GENERIC_PATTERN = re.compile(r"^/documents/(Rule-\d+(?:\.\d+)?)\.pdf$")


def redirect_uri(uri):
    # Match amended/suffixed rule filenames
    if REDIRECT_PATTERN.match(uri):
        match = STRIP_PATTERN.match(uri)
        if match:
            return f"/documents/{match.group(1).lower()}.pdf"

    # Match generic rule PDFs like Rule-101.pdf
    match = GENERIC_PATTERN.match(uri)
    if match:
        return f"/documents/{match.group(1).lower()}.pdf"

    return None


@pytest.mark.parametrize(
    "uri, expected",
    [
        (
            "/documents/Rule-100-Amended_2023.pdf",
            "/documents/rule-100.pdf",
        ),  # keyword-based redirect
        (
            "/documents/Rule-10superseded.pdf",
            "/documents/rule-10.pdf",
        ),  # keyword-based redirect
        (
            "/documents/Rule-255.2New.pdf",
            "/documents/rule-255.2.pdf",
        ),  # keyword-based redirect
        (
            "/documents/Rule-101.pdf",
            "/documents/rule-101.pdf",
        ),  # generic lowercase redirect
        ("/documents/AnotherDoc.pdf", None),  # non-matching
    ],
)
def test_redirect_uri_transforms(uri, expected):
    assert redirect_uri(uri) == expected
