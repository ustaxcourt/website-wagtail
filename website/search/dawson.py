import re
from dataclasses import dataclass

# nnn-yya: nnn is 3-6 digits, yy is a two-digit year, a is 0-2 letters.
DOCKET_NUMBER_PATTERN = re.compile(r"\d{3,6}-\d{2}[a-zA-Z]{0,2}")

# A search term made up of nothing but digits and dashes.
DIGITS_AND_DASHES_PATTERN = re.compile(r"^[0-9-]+$")

# SSNs (XXX-XX-XXXX) are explicitly excepted from the invalid-docket warning.
SSN_LIKE_PATTERN = re.compile(r"^\d{3}-\d{2}-\d{4}$")


@dataclass(frozen=True)
class DocketMatch:
    """Result of checking a search term against the USTC docket number format."""

    term: str
    docket_number: str | None
    is_valid: bool


def is_docket_number(term: str) -> DocketMatch | None:
    """
    Check whether `term` conforms to, or looks like an attempt at, a USTC
    docket number (format: nnn-yya, e.g. "123-19" or "5695-23X"), including
    as a substring of a longer search term (e.g. "Docket No 123-19").

    Returns:
        None: `term` doesn't look like a docket-number attempt at all.
        DocketMatch(is_valid=True, docket_number=...): `term` contains a
            substring matching the docket number format.
        DocketMatch(is_valid=False, docket_number=None): `term` is entirely
            digits/dashes but doesn't contain a valid docket number, and
            isn't an SSN-shaped exception (XXX-XX-XXXX) — this should
            trigger the "invalid docket number" warning.

    SSN-shaped terms (XXX-XX-XXXX) are excepted entirely per the AC: an SSN's
    first 6 characters happen to fit the nnn-yy shape (e.g. "111-11" out of
    "111-11-1111"), so the SSN check must run before the substring match
    below, not just before the invalid-format warning.
    """
    if SSN_LIKE_PATTERN.match(term):
        return None

    match = DOCKET_NUMBER_PATTERN.search(term)
    if match:
        return DocketMatch(term=term, docket_number=match.group(0), is_valid=True)

    if DIGITS_AND_DASHES_PATTERN.match(term) or "docket" in term.lower():
        return DocketMatch(term=term, docket_number=None, is_valid=False)

    return None
