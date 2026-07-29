from dataclasses import dataclass


@dataclass(frozen=True)
class DocketMatch:
    """Result of checking a search term against the USTC docket number format."""

    term: str
    docket_number: str | None
    is_valid: bool


def is_docket_number(term: str) -> DocketMatch | None:
    """
    Check whether `term` conforms to, or looks like an attempt at, a USTC
    docket number (format: nnn-yya, e.g. "123-19" or "5695-23X").

    Returns:
        None: `term` doesn't look like a docket-number attempt at all.
        DocketMatch(is_valid=True, docket_number=...): `term` matches the
            docket number format exactly.
        DocketMatch(is_valid=False, docket_number=None): `term` looks like a
            docket-number attempt (digits/dashes) but doesn't conform to the
            format, and should trigger the "invalid docket number" warning.

    TODO(WAG-50): implement docket-number detection regex. Until this lands,
    always returns None so docket detection stays inert (regular search is
    unaffected) rather than raising on every search request.
    """
    return None
