import os
import sys
import re
import django
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

# Predefined hard redirects
HARDCODED_REDIRECTS = {
    "/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf": "/files/documents/Complete-Rules-of-Practice-and-Procedure.pdf",
    "/documents/Rule-229A.pdf": "/files/documents/rule-229A.pdf",
    "/documents/Rule-2302nd-amended.pdf": "/files/documents/rule-230.pdf",
    "/documents/Rule-255.1_amended_08082024.pdf": "/files/documents/rule-255.1.pdf",
    "/documents/Rule-255.2New.pdf": "/files/documents/rule-255.2.pdf",
    "/documents/Rule-255.3New.pdf": "/files/documents/rule-255.3.pdf",
    "/documents/Rule-255.4New.pdf": "/files/documents/rule-255.4.pdf",
    "/documents/Rule-255.5New.pdf": "/files/documents/rule-255.5.pdf",
    "/documents/Rule-255.6New.pdf": "/files/documents/rule-255.6.pdf",
    "/documents/Rule-255.7New.pdf": "/files/documents/rule-255.7.pdf",
}

# Regex patterns
REDIRECT_PATTERN = re.compile(
    r"^/documents/Rule-\d+[.\-_A-Za-z0-9]*?(amended|Amended|superseded|2nd|2nd-amended|New|new)[^/]*\.pdf$"
)
STRIP_PATTERN = re.compile(r"^/documents/(Rule-\d+(?:\.\d+)?)[\w.\-]*\.pdf$")
GENERIC_PATTERN = re.compile(r"^/documents/(Rule-\d+(?:\.\d+)?)\.pdf$")


def redirect_uri(uri):
    if uri.startswith("/files/"):
        uri = uri[len("/files") :]

    # Check hardcoded map first
    if uri in HARDCODED_REDIRECTS:
        return HARDCODED_REDIRECTS[uri].replace("/documents/Rule-", "/documents/rule-")

    # Regex-based legacy cleanup
    if REDIRECT_PATTERN.match(uri):
        match = STRIP_PATTERN.match(uri)
        if match:
            new_uri = f"/documents/{match.group(1)}.pdf"
            return "/files" + new_uri.replace("/documents/Rule-", "/documents/rule-")

    # Case-normalization only
    match = GENERIC_PATTERN.match(uri)
    if match:
        new_uri = f"/documents/{match.group(1)}.pdf"
        return "/files" + new_uri.replace("/documents/Rule-", "/documents/rule-")

    return None


@pytest.mark.parametrize(
    "uri, expected",
    [
        ("/files/documents/Rule-100-Amended_2023.pdf", "/files/documents/rule-100.pdf"),
        ("/files/documents/Rule-10superseded.pdf", "/files/documents/rule-10.pdf"),
        ("/files/documents/Rule-255.2New.pdf", "/files/documents/rule-255.2.pdf"),
        ("/files/documents/Rule-101.pdf", "/files/documents/rule-101.pdf"),
        ("/files/documents/AnotherDoc.pdf", None),
        (
            "/files/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf",
            "/files/documents/Complete-Rules-of-Practice-and-Procedure.pdf",
        ),
    ],
)
def test_redirect_uri_transforms(uri, expected):
    assert redirect_uri(uri) == expected
