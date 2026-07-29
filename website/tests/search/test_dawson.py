"""Tests for search/dawson.py — the docket-number detection seam.

The detection regex is intentionally not implemented yet (WAG-50); these
tests pin down the current inert placeholder behavior so that filling in
the real regex is a deliberate, visible change rather than a silent one.
"""

from search.dawson import is_docket_number


def test_is_docket_number_is_currently_inert():
    assert is_docket_number("123-19") is None
    assert is_docket_number("not a docket number") is None
    assert is_docket_number("") is None
