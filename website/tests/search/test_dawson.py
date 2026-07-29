"""Tests for search/dawson.py — the docket-number detection seam."""

from search.dawson import DocketMatch, is_docket_number


class TestIsDocketNumber:
    def test_exact_docket_number_is_valid(self):
        result = is_docket_number("123-19")
        assert result == DocketMatch(
            term="123-19", docket_number="123-19", is_valid=True
        )

    def test_docket_number_with_letter_suffix_is_valid(self):
        result = is_docket_number("5695-23X")
        assert result.is_valid is True
        assert result.docket_number == "5695-23X"

    def test_docket_number_as_substring_of_longer_term_is_valid(self):
        result = is_docket_number("Docket No 123-19 please")
        assert result.is_valid is True
        assert result.docket_number == "123-19"

    def test_non_numeric_term_is_not_a_docket_attempt(self):
        assert is_docket_number("tax court rules") is None

    def test_empty_string_is_not_a_docket_attempt(self):
        assert is_docket_number("") is None

    def test_digits_without_dash_is_invalid_format(self):
        result = is_docket_number("1234567890")
        assert result == DocketMatch(
            term="1234567890", docket_number=None, is_valid=False
        )

    def test_too_few_leading_digits_is_invalid_format(self):
        # Only 2 digits before the dash; the format requires 3-6.
        result = is_docket_number("12-3456789")
        assert result == DocketMatch(
            term="12-3456789", docket_number=None, is_valid=False
        )

    def test_ssn_shaped_input_is_excepted_from_warning(self):
        # XXX-XX-XXXX is explicitly excluded from the "invalid docket
        # number" warning per the AC.
        assert is_docket_number("111-11-1111") is None

    def test_term_with_letters_and_digits_but_no_dash_is_not_a_docket_attempt(self):
        assert is_docket_number("case123") is None
