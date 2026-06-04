"""Tests for home/templatetags/filters.py"""

from django.utils import timezone
from datetime import datetime

from home.templatetags.filters import (
    column_width,
    get_type,
    parse_iso_date,
    slugify_text,
)


class TestColumnWidth:
    def test_12_cols_1_column(self):
        assert column_width(1) == 12

    def test_12_cols_2_columns(self):
        assert column_width(2) == 6

    def test_12_cols_3_columns(self):
        assert column_width(3) == 4

    def test_12_cols_4_columns(self):
        assert column_width(4) == 3

    def test_12_cols_6_columns(self):
        assert column_width(6) == 2


class TestGetTypeFilter:
    def test_string(self):
        assert get_type("hello") == "str"

    def test_integer(self):
        assert get_type(1) == "int"

    def test_list(self):
        assert get_type([]) == "list"

    def test_dict(self):
        assert get_type({}) == "dict"


class TestParseIsoDate:
    def test_none_returns_none(self):
        assert parse_iso_date(None) is None

    def test_empty_string_returns_none(self):
        assert parse_iso_date("") is None

    def test_valid_iso_string_returns_aware_datetime(self):
        result = parse_iso_date("2024-06-01T12:00:00")
        assert result is not None
        assert timezone.is_aware(result)

    def test_valid_iso_string_with_tz_returns_aware_datetime(self):
        result = parse_iso_date("2024-06-01T12:00:00+00:00")
        assert result is not None
        assert timezone.is_aware(result)

    def test_invalid_string_returns_input(self):
        result = parse_iso_date("not-a-date")
        assert result == "not-a-date"

    def test_non_string_passed_through(self):
        dt = datetime(2024, 6, 1, 12, 0, 0)
        result = parse_iso_date(dt)
        assert result == dt


class TestSlugifyText:
    def test_simple_text(self):
        assert slugify_text("Hello World") == "hello-world"

    def test_text_with_special_chars(self):
        assert slugify_text("Héllo Wörld") == "hello-world"

    def test_already_slug(self):
        assert slugify_text("hello-world") == "hello-world"

    def test_empty_string(self):
        assert slugify_text("") == ""

    def test_numbers(self):
        assert slugify_text("Section 42") == "section-42"
