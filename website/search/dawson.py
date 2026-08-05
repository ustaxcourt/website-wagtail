import re
from dataclasses import dataclass

# nnn-yya: nnn is 3-6 digits, yy is a two-digit year, a is 0-2 letters.
# Bounded on both sides so it can't match a fragment of a longer digit run
# (e.g. "566-555" shouldn't match "566-55" as if 55 were a real two-digit
# year — the next character being another digit means it isn't).
DOCKET_NUMBER_PATTERN = re.compile(r"(?<!\d)\d{3,6}-\d{2}[a-zA-Z]{0,2}(?!\d)")

# A search term that starts with a digit.
STARTS_WITH_DIGIT_PATTERN = re.compile(r"^\d")

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
        DocketMatch(is_valid=False, docket_number=None): `term` starts with
            a digit but doesn't contain a valid docket number, and isn't an
            SSN-shaped exception (XXX-XX-XXXX) — this should trigger the
            "invalid docket number" warning. (Relaxed per 2026-08-03
            update: previously required the whole term to be digits/dashes;
            now any term starting with a digit qualifies. This only affects
            when the warning shows — it does not change when a term is
            treated as a valid docket number and passed to the DAWSON
            lookup, which is still decided by the substring match above.)

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

    if STARTS_WITH_DIGIT_PATTERN.match(term):
        return DocketMatch(term=term, docket_number=None, is_valid=False)

    return None
