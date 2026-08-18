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

    def test_term_starting_with_digit_containing_letters_is_invalid_format(self):
        # Relaxed per 2026-08-03 update: the warning no longer requires the
        # whole term to be digits/dashes — starting with a digit is enough.
        result = is_docket_number("123 tax rules")
        assert result == DocketMatch(
            term="123 tax rules", docket_number=None, is_valid=False
        )

    def test_term_with_digit_not_at_start_is_not_a_docket_attempt(self):
        # A digit appearing later in the term (not at the start) still
        # doesn't trigger the warning — it must start with a digit.
        assert is_docket_number("tax 123 rules") is None

    def test_relaxed_warning_does_not_affect_valid_docket_detection(self):
        # The substring-match path (is_valid=True, passed to DAWSON) is
        # unchanged by the relaxed warning condition.
        result = is_docket_number("123-19 tax rules")
        assert result == DocketMatch(
            term="123-19 tax rules", docket_number="123-19", is_valid=True
        )

    def test_trailing_extra_digit_after_year_is_invalid_format(self):
        # "566-55" isn't a real two-digit year here — it's a fragment of
        # "555". The whole "566-555" should trigger the warning, not get
        # matched as if "566-55" were a valid docket number.
        result = is_docket_number("566-555")
        assert result == DocketMatch(term="566-555", docket_number=None, is_valid=False)

    def test_leading_extra_digits_before_docket_number_is_invalid_format(self):
        # Symmetric case: an 8-digit run before the dash means no clean
        # 3-6 digit nnn boundary exists anywhere in it.
        result = is_docket_number("12345678-19")
        assert result == DocketMatch(
            term="12345678-19", docket_number=None, is_valid=False
        )

    def test_pasted_leading_whitespace_still_shows_invalid_format_warning(self):
        # Pasted search terms often carry leading whitespace (e.g. copied
        # from a PDF or table cell). A leading space previously defeated
        # the "starts with a digit" check (anchored to literal string
        # start), silently suppressing the warning for pasted input.
        result = is_docket_number(" 444-444")
        assert result == DocketMatch(term="444-444", docket_number=None, is_valid=False)

    def test_pasted_trailing_whitespace_still_shows_invalid_format_warning(self):
        result = is_docket_number("444-444 ")
        assert result == DocketMatch(term="444-444", docket_number=None, is_valid=False)

    def test_pasted_tab_and_newline_whitespace_still_shows_invalid_format_warning(
        self,
    ):
        result = is_docket_number("\t444-444\n")
        assert result == DocketMatch(term="444-444", docket_number=None, is_valid=False)

    def test_pasted_non_breaking_space_still_shows_invalid_format_warning(self):
        # \xa0 is a common artifact of pasting from web pages/PDFs.
        result = is_docket_number("\xa0444-444")
        assert result == DocketMatch(term="444-444", docket_number=None, is_valid=False)

    def test_pasted_leading_whitespace_around_valid_docket_still_matches(self):
        result = is_docket_number("  124-26  ")
        assert result == DocketMatch(
            term="124-26", docket_number="124-26", is_valid=True
        )

    def test_pasted_leading_whitespace_around_ssn_still_excepted(self):
        assert is_docket_number("  111-11-1111  ") is None

    def test_search_for_docket_at_beginning_of_term_shows_invalid_format_warning(self):
        result = is_docket_number("Docket 1")
        assert result == DocketMatch(
            term="Docket 1", docket_number=None, is_valid=False
        )

    def test_search_for_mixed_case_docket_at_beginning_of_term_shows_invalid_format_warning(
        self,
    ):
        result = is_docket_number("DoCkeT 1")
        assert result == DocketMatch(
            term="DoCkeT 1", docket_number=None, is_valid=False
        )

    def test_search_for_docket_in_middle_of_term_shows_invalid_format_warning(self):
        result = is_docket_number("Judge Urda docket 1")
        assert result == DocketMatch(
            term="Judge Urda docket 1", docket_number=None, is_valid=False
        )

    def test_search_for_mixed_case_docket_in_middle_of_term_shows_invalid_format_warning(
        self,
    ):
        result = is_docket_number("Judge Urda dOCkEt 1")
        assert result == DocketMatch(
            term="Judge Urda dOCkEt 1", docket_number=None, is_valid=False
        )

    def test_search_for_docket_in_middle_of_a_word_in_term_is_not_a_docket_attempt(
        self,
    ):
        assert is_docket_number("docketing 1") is None
