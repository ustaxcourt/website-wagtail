"""
Tests for the helper functions in home/views.py.
These are pure functions (no DB required) that can be tested directly.
"""

import pytest
from datetime import datetime, date, timezone as dt_timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from django.utils import timezone

from home.views import (
    get_title,
    get_publish_date,
    get_publish_date_raw,
    get_homepage_expiration,
    get_homepage_expiration_raw,
    get_created_at,
    format_category,
    to_default_tz,
    NewsItemReportView,
)


def make_news_item(**kwargs):
    """Create a mock NewsItem (not a banner)."""
    defaults = {
        "_is_banner": False,
        "title": "Test News Item",
        "publish_date": timezone.now(),
        "homepage_display_expiration_date": None,
        "created_at": timezone.now(),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_banner(**kwargs):
    """Create a mock Banner object."""
    defaults = {
        "_is_banner": True,
        "banner_title": "Test Banner",
        "priority_level": "high",
        "banner_start_date": timezone.now(),
        "banner_end_date": None,
        "first_published_at": timezone.now(),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# get_title
# ---------------------------------------------------------------------------


class TestGetTitle:
    def test_news_item_returns_title(self):
        obj = make_news_item(title="My Article")
        assert get_title(obj) == "My Article"

    def test_news_item_empty_title_returns_dash(self):
        obj = make_news_item(title="")
        assert get_title(obj) == "-"

    def test_news_item_no_title_attr_returns_dash(self):
        obj = SimpleNamespace(_is_banner=False)
        assert get_title(obj) == "-"

    def test_high_priority_banner_title(self):
        obj = make_banner(priority_level="high", banner_title="Alert")
        assert get_title(obj) == "High priority banner: Alert"

    def test_critical_banner_title(self):
        obj = make_banner(priority_level="critical", banner_title="Emergency")
        assert get_title(obj) == "Critical banner: Emergency"

    def test_obj_with_no_is_banner_uses_title(self):
        obj = SimpleNamespace(title="Plain")
        assert get_title(obj) == "Plain"


# ---------------------------------------------------------------------------
# format_category
# ---------------------------------------------------------------------------


class TestFormatCategory:
    def test_news_item_category(self):
        obj = make_news_item()
        assert format_category(obj) == "News Item"

    def test_high_priority_banner_category(self):
        obj = make_banner(priority_level="high")
        assert format_category(obj) == "High Priority Announcement"

    def test_critical_banner_category(self):
        obj = make_banner(priority_level="critical")
        assert format_category(obj) == "Critical Announcement"

    def test_banner_with_no_priority_level(self):
        obj = make_banner(priority_level="none")
        assert format_category(obj) == "Banner"

    def test_object_without_is_banner_is_news_item(self):
        obj = SimpleNamespace(title="Foo")
        assert format_category(obj) == "News Item"


# ---------------------------------------------------------------------------
# get_publish_date / get_publish_date_raw
# ---------------------------------------------------------------------------


class TestGetPublishDate:
    def test_news_item_with_date(self):
        dt = timezone.now()
        obj = make_news_item(publish_date=dt)
        assert get_publish_date(obj) == dt
        assert get_publish_date_raw(obj) == dt

    def test_news_item_no_publish_date_returns_dash(self):
        obj = SimpleNamespace(_is_banner=False)
        assert get_publish_date(obj) == "-"

    def test_news_item_null_publish_date_returns_dash(self):
        obj = make_news_item(publish_date=None)
        assert get_publish_date(obj) == "-"

    def test_banner_returns_banner_start_date(self):
        dt = timezone.now()
        obj = make_banner(banner_start_date=dt)
        assert get_publish_date(obj) == dt
        assert get_publish_date_raw(obj) == dt

    def test_banner_null_start_date_returns_dash(self):
        obj = make_banner(banner_start_date=None)
        assert get_publish_date(obj) == "-"

    def test_banner_raw_null_returns_none(self):
        obj = make_banner(banner_start_date=None)
        assert get_publish_date_raw(obj) is None


# ---------------------------------------------------------------------------
# get_homepage_expiration / get_homepage_expiration_raw
# ---------------------------------------------------------------------------


class TestGetHomepageExpiration:
    def test_news_item_with_expiration(self):
        dt = timezone.now()
        obj = make_news_item(homepage_display_expiration_date=dt)
        assert get_homepage_expiration(obj) == dt
        assert get_homepage_expiration_raw(obj) == dt

    def test_news_item_null_expiration_returns_dash(self):
        obj = make_news_item(homepage_display_expiration_date=None)
        assert get_homepage_expiration(obj) == "-"

    def test_news_item_no_expiration_attr_returns_dash(self):
        obj = SimpleNamespace(_is_banner=False)
        assert get_homepage_expiration(obj) == "-"

    def test_banner_returns_end_date(self):
        dt = timezone.now()
        obj = make_banner(banner_end_date=dt)
        assert get_homepage_expiration(obj) == dt
        assert get_homepage_expiration_raw(obj) == dt

    def test_banner_null_end_date_returns_dash(self):
        obj = make_banner(banner_end_date=None)
        assert get_homepage_expiration(obj) == "-"

    def test_banner_raw_null_returns_none(self):
        obj = make_banner(banner_end_date=None)
        assert get_homepage_expiration_raw(obj) is None


# ---------------------------------------------------------------------------
# get_created_at
# ---------------------------------------------------------------------------


class TestGetCreatedAt:
    def test_news_item_returns_created_at(self):
        dt = timezone.now()
        obj = make_news_item(created_at=dt)
        assert get_created_at(obj) == dt

    def test_news_item_no_created_at_returns_dash(self):
        obj = SimpleNamespace(_is_banner=False)
        assert get_created_at(obj) == "-"

    def test_banner_returns_first_published_at(self):
        dt = timezone.now()
        obj = make_banner(first_published_at=dt)
        assert get_created_at(obj) == dt

    def test_banner_null_first_published_returns_dash(self):
        obj = make_banner(first_published_at=None)
        assert get_created_at(obj) == "-"


# ---------------------------------------------------------------------------
# to_default_tz
# ---------------------------------------------------------------------------


class TestToDefaultTz:
    def test_none_returns_none(self):
        assert to_default_tz(None) is None

    def test_naive_datetime_returned_as_is(self):
        naive = datetime(2024, 6, 1, 12, 0, 0)
        result = to_default_tz(naive)
        assert result == naive

    def test_aware_datetime_converted_to_naive(self):
        aware = datetime(2024, 6, 1, 12, 0, 0, tzinfo=dt_timezone.utc)
        result = to_default_tz(aware)
        # Result should be naive (tzinfo is None)
        assert result.tzinfo is None


# ---------------------------------------------------------------------------
# NewsItemReportView.get_queryset / get_filtered_queryset
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestNewsItemReportViewHelpers:
    def test_get_filename_contains_date(self):
        view = NewsItemReportView()
        filename = view.get_filename()
        today = date.today().strftime("%Y-%m-%d")
        assert today in filename
        assert "News_and_Announcements_Report" in filename

    def test_get_heading_uses_export_headings(self):
        view = NewsItemReportView()
        assert view.get_heading([], "id") == "ID"
        assert view.get_heading([], "title") == "Title"
        assert view.get_heading([], "category") == "Category"

    def test_get_heading_unknown_field_titlized(self):
        view = NewsItemReportView()
        assert view.get_heading([], "some_field") == "Some Field"

    def test_get_queryset_empty_db_returns_empty_list(self):
        view = NewsItemReportView()
        result = view.get_queryset()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_filtered_queryset_empty_filters(self):
        from django.test import RequestFactory

        view = NewsItemReportView()
        view.request = RequestFactory().get("/")
        queryset = view.get_queryset()
        result = view.get_filtered_queryset(queryset=queryset, filters={})
        assert result == queryset

    def test_to_row_dict_news_item(self):
        view = NewsItemReportView()
        obj = make_news_item(
            id=1,
            title="My News",
            publish_date=timezone.now(),
            homepage_display_expiration_date=None,
        )
        # Add attribute expected by to_row_dict
        obj.document_url = "http://example.com/doc.pdf"
        row = view.to_row_dict(obj)
        assert row["title"] == "My News"
        assert row["category"] == "News Item"

    def test_to_row_dict_banner(self):
        view = NewsItemReportView()
        obj = make_banner(
            id=2,
            priority_level="high",
            banner_title="Alert",
            banner_start_date=timezone.now(),
            banner_end_date=None,
        )
        row = view.to_row_dict(obj)
        assert row["category"] == "High Priority Announcement"
        assert "Alert" in row["title"]


class TestNewsItemReportViewFilters:
    def make_view(self):
        from home.views import NewsItemReportView
        from django.test import RequestFactory

        view = NewsItemReportView()
        view.request = RequestFactory().get("/")
        return view

    def test_filter_by_title_returns_matching_items(self):
        view = self.make_view()
        item1 = make_news_item(title="Alpha News")
        item2 = make_news_item(title="Beta News")
        result = view.get_filtered_queryset(
            queryset=[item1, item2], filters={"title": "Alpha"}
        )
        assert item1 in result
        assert item2 not in result

    def test_filter_by_created_at_returns_matching_items(self):
        view = self.make_view()
        from django.utils import timezone

        dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        item1 = make_news_item(created_at=dt)
        item2 = make_news_item(created_at=dt.replace(year=dt.year - 1))
        filters = {"created_at": dt.strftime("%Y-%m-%d")}
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 in result
        assert item2 not in result

    def test_filter_by_publish_date_range_from(self):
        view = self.make_view()
        from django.utils import timezone

        dt1 = timezone.now()
        dt2 = dt1.replace(year=dt1.year - 1)
        item1 = make_news_item(publish_date=dt1)
        item2 = make_news_item(publish_date=dt2)
        filters = {"publish_date_range_from": dt1.strftime("%Y-%m-%d")}
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 in result
        assert item2 not in result

    def test_filter_by_publish_date_range_to(self):
        view = self.make_view()
        from django.utils import timezone

        dt1 = timezone.now()
        dt2 = dt1.replace(year=dt1.year + 1)
        item1 = make_news_item(publish_date=dt1)
        item2 = make_news_item(publish_date=dt2)
        filters = {"publish_date_range_to": dt1.strftime("%Y-%m-%d")}
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 in result
        assert item2 not in result

    def test_filter_publish_date_with_none_value_excluded(self):
        view = self.make_view()
        from django.utils import timezone

        dt = timezone.now()
        item1 = make_news_item(publish_date=None)
        item2 = make_news_item(publish_date=dt)
        filters = {"publish_date_range_from": dt.strftime("%Y-%m-%d")}
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 not in result

    def test_filter_by_homepage_date_range_from(self):
        view = self.make_view()
        from django.utils import timezone

        dt1 = timezone.now()
        dt2 = dt1.replace(year=dt1.year - 1)
        item1 = make_news_item(homepage_display_expiration_date=dt1)
        item2 = make_news_item(homepage_display_expiration_date=dt2)
        filters = {
            "homepage_display_expiration_date_range_from": dt1.strftime("%Y-%m-%d")
        }
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 in result
        assert item2 not in result

    def test_filter_by_homepage_date_range_to(self):
        view = self.make_view()
        from django.utils import timezone

        dt1 = timezone.now()
        dt2 = dt1.replace(year=dt1.year + 1)
        item1 = make_news_item(homepage_display_expiration_date=dt1)
        item2 = make_news_item(homepage_display_expiration_date=dt2)
        filters = {
            "homepage_display_expiration_date_range_to": dt1.strftime("%Y-%m-%d")
        }
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 in result
        assert item2 not in result

    def test_filter_homepage_date_none_excluded(self):
        view = self.make_view()
        from django.utils import timezone

        dt = timezone.now()
        item1 = make_news_item(homepage_display_expiration_date=None)
        item2 = make_news_item(homepage_display_expiration_date=dt)
        filters = {
            "homepage_display_expiration_date_range_from": dt.strftime("%Y-%m-%d")
        }
        result = view.get_filtered_queryset(queryset=[item1, item2], filters=filters)
        assert item1 not in result

    def test_get_heading_with_override(self):
        view = self.make_view()
        # The export_headings dict should have entries
        for field, override in view.export_headings.items():
            result = view.get_heading([], field)
            assert result == override
            break  # just test one

    def test_get_heading_fallback(self):
        view = self.make_view()
        result = view.get_heading([], "some_custom_field")
        assert result == "Some Custom Field"


class TestSVGAndPDFChooserViews:
    def test_svg_chooser_viewset_filters_svg(self):
        from home.views import SVGChooseView
        from unittest.mock import patch

        view = SVGChooseView.__new__(SVGChooseView)
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        with patch.object(
            SVGChooseView.__bases__[0] if SVGChooseView.__bases__ else object,
            "get_object_list",
            return_value=mock_qs,
            create=True,
        ):
            with patch(
                "wagtail.documents.views.chooser.DocumentChooserViewSet.choose_view_class.get_object_list",
                return_value=mock_qs,
            ):
                view.get_object_list()
        mock_qs.filter.assert_called_once_with(file__iendswith=".svg")

    def test_pdf_chooser_viewset_filters_pdf(self):
        from home.views import PDFChooseView
        from unittest.mock import patch

        view = PDFChooseView.__new__(PDFChooseView)
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        with patch(
            "wagtail.documents.views.chooser.DocumentChooserViewSet.choose_view_class.get_object_list",
            return_value=mock_qs,
        ):
            view.get_object_list()
        mock_qs.filter.assert_called_once_with(file__iendswith=".pdf")
