"""Tests for home/views.py — report views and filter sets."""

import pytest
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from django.utils import timezone


def make_news_item(**kwargs):
    defaults = {
        "_is_banner": False,
        "title": "Test News Item",
        "publish_date": timezone.now(),
        "homepage_display_expiration_date": None,
        "created_at": timezone.now(),
        "document_url": "-",
        "id": 1,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_banner(**kwargs):
    defaults = {
        "_is_banner": True,
        "banner_title": "Test Banner",
        "priority_level": "high",
        "banner_start_date": timezone.now(),
        "banner_end_date": None,
        "first_published_at": timezone.now(),
        "id": 2,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# NewsItemReportView.get_filtered_queryset — created_at filter
# ---------------------------------------------------------------------------


class TestNewsItemReportViewCreatedAtFilter:
    def _make_view(self):
        from home.views import NewsItemReportView

        view = NewsItemReportView()
        view.request = RequestFactory().get("/")
        return view

    def test_filter_by_created_at_matches_item(self):
        view = self._make_view()
        dt = timezone.now()
        item1 = make_news_item(created_at=dt)
        item2 = make_news_item(created_at=dt.replace(year=dt.year - 1))
        result = view.get_filtered_queryset(
            queryset=[item1, item2],
            filters={"created_at": dt.strftime("%Y-%m-%d")},
        )
        assert item1 in result
        assert item2 not in result

    def test_filter_by_created_at_no_match_returns_empty(self):
        view = self._make_view()
        dt = timezone.now()
        item = make_news_item(created_at=dt.replace(year=dt.year - 1))
        result = view.get_filtered_queryset(
            queryset=[item],
            filters={"created_at": dt.strftime("%Y-%m-%d")},
        )
        assert item not in result

    def test_publish_date_without_date_method_excluded(self):
        """Covers branch where pub_date has no .date() method (e.g. raw date object)."""
        view = self._make_view()
        now = timezone.now()
        item_no_date_method = make_news_item(publish_date=now.date())
        filters = {"publish_date_range_from": now.strftime("%Y-%m-%d")}
        result = view.get_filtered_queryset(
            queryset=[item_no_date_method], filters=filters
        )
        assert item_no_date_method in result

    def test_homepage_date_without_date_method_excluded(self):
        """Covers branch where exp_date has no .date() method (e.g. raw date object)."""
        view = self._make_view()
        now = timezone.now()
        item = make_news_item(homepage_display_expiration_date=now.date())
        filters = {
            "homepage_display_expiration_date_range_from": now.strftime("%Y-%m-%d")
        }
        result = view.get_filtered_queryset(queryset=[item], filters=filters)
        assert item in result


# ---------------------------------------------------------------------------
# SearchDefinitionsReportFilterSet.filter_in_list
# ---------------------------------------------------------------------------


class TestSearchDefinitionsFilterInList:
    def _make_filterset(self):
        from home.views import SearchDefinitionsReportFilterSet

        fs = SearchDefinitionsReportFilterSet.__new__(SearchDefinitionsReportFilterSet)
        return fs

    def test_filter_in_list_yes_filters_to_word_list(self):
        fs = self._make_filterset()
        qs = MagicMock()
        qs.annotate.return_value = qs
        qs.filter.return_value = qs

        with patch(
            "home.views.DefinitionsPage.getWordList",
            return_value=["petitioner", "respondent"],
        ):
            fs.filter_in_list(qs, "in_list", "yes")
        qs.filter.assert_called_once()

    def test_filter_in_list_no_excludes_word_list(self):
        fs = self._make_filterset()
        qs = MagicMock()
        qs.annotate.return_value = qs
        qs.exclude.return_value = qs

        with patch(
            "home.views.DefinitionsPage.getWordList", return_value=["petitioner"]
        ):
            fs.filter_in_list(qs, "in_list", "no")
        qs.exclude.assert_called_once()

    def test_filter_in_list_other_value_returns_original_queryset(self):
        fs = self._make_filterset()
        qs = MagicMock()

        with patch(
            "home.views.DefinitionsPage.getWordList", return_value=["petitioner"]
        ):
            result = fs.filter_in_list(qs, "in_list", "all")
        assert result is qs


# ---------------------------------------------------------------------------
# SearchDefinitionsReportView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSearchDefinitionsReportView:
    def test_get_queryset_returns_queryset(self):
        from home.views import SearchDefinitionsReportView

        view = SearchDefinitionsReportView()
        qs = view.get_queryset()
        assert qs is not None

    def test_get_filename_contains_date(self):
        from home.views import SearchDefinitionsReportView

        view = SearchDefinitionsReportView()
        filename = view.get_filename()
        today = date.today().strftime("%Y-%m-%d")
        assert today in filename
        assert "Search_Terms_Report" in filename


# ---------------------------------------------------------------------------
# PrivateSeminarDisclosureReportView
# ---------------------------------------------------------------------------


class TestPrivateSeminarDisclosureReportView:
    def _make_view(self):
        from home.views import PrivateSeminarDisclosureReportView

        view = PrivateSeminarDisclosureReportView()
        view.request = RequestFactory().get("/")
        return view

    def test_to_row_dict_builds_correct_dict(self):
        view = self._make_view()
        item = MagicMock()
        item.judge.display_name = "Judge Smith"
        item.program_provider = "ACME Corp"
        item.program_title = "Tax Law 101"
        item.date = date(2024, 6, 1)
        item.location = "Washington, DC"
        item.program_topics = "<p>Tax procedures</p>"
        item.supporter = "Tax Foundation"

        row = view.to_row_dict(item)
        assert row["judge_name"] == "Judge Smith"
        assert row["program_provider"] == "ACME Corp"
        assert row["date"] == date(2024, 6, 1)
        assert "Tax procedures" in row["program_topics"]
        assert row["supporter"] == "Tax Foundation"

    def test_to_row_dict_empty_program_topics(self):
        view = self._make_view()
        item = MagicMock()
        item.judge.display_name = "Judge Jones"
        item.program_provider = "Corp"
        item.program_title = "Title"
        item.date = date(2024, 1, 1)
        item.location = "NYC"
        item.program_topics = ""
        item.supporter = None

        row = view.to_row_dict(item)
        assert row["program_topics"] == ""
        assert row["supporter"] == ""

    def test_get_heading_known_field(self):
        view = self._make_view()
        result = view.get_heading([], "judge_name")
        assert result == "Judge Name"

    def test_get_heading_unknown_field_titlizes(self):
        view = self._make_view()
        result = view.get_heading([], "some_custom_field")
        assert result == "Some Custom Field"

    def test_get_filename_with_mocked_settings(self):
        view = self._make_view()

        mock_settings = MagicMock()
        mock_settings.disclosure_years = 3

        with patch(
            "home.models.settings.PrivateSeminarDisclosureSettings.load",
            return_value=mock_settings,
        ):
            filename = view.get_filename()
        assert "3" in filename
        assert "Private_Seminar_Disclosure" in filename

    def test_get_cutoff_handles_leap_year_edge_case(self):
        """Covers the except ValueError branch in _get_cutoff (Feb 29 edge case)."""
        view = self._make_view()

        mock_settings = MagicMock()
        mock_settings.disclosure_years = 3

        mock_today = MagicMock(spec=date)
        mock_today.year = 2024
        mock_today.replace.side_effect = [ValueError("invalid date"), date(2021, 2, 28)]

        with patch(
            "home.models.settings.PrivateSeminarDisclosureSettings.load",
            return_value=mock_settings,
        ):
            with patch("home.views.date") as mock_date_cls:
                mock_date_cls.today.return_value = mock_today
                result = view._get_cutoff()
        assert result == date(2021, 2, 28)


# ---------------------------------------------------------------------------
# CustomExternalLinksReportView
# ---------------------------------------------------------------------------


class TestCustomExternalLinksReportView:
    def _make_view(self):
        from home.views import CustomExternalLinksReportView

        view = CustomExternalLinksReportView()
        view.request = RequestFactory().get("/")
        view.is_export = False
        return view

    def test_get_extractor_returns_custom_extractor(self):
        from home.utils.custom_link_extractor import CustomLinkExtractor

        view = self._make_view()
        extractor = view.get_extractor()
        assert isinstance(extractor, CustomLinkExtractor)

    def test_get_context_data_adds_external_links(self):
        view = self._make_view()
        mock_page = MagicMock()
        mock_extractor = MagicMock()
        mock_extractor.extract_from_page.return_value = [
            {"text": "Example", "url": "https://example.com"}
        ]

        mock_context = {"object_list": [mock_page]}

        with patch(
            "wagtail.admin.views.generic.base.BaseListingView.get_context_data",
            return_value=mock_context,
        ):
            with patch.object(view, "get_extractor", return_value=mock_extractor):
                view.get_context_data()

        assert hasattr(mock_page, "external_links")
        assert len(mock_page.external_links) == 1

    def test_get_context_data_export_mode(self):
        view = self._make_view()
        view.is_export = True
        mock_page = MagicMock()
        mock_page.title = "Tax Page"
        mock_page.slug = "tax-page"
        mock_extractor = MagicMock()
        mock_extractor.extract_from_page.return_value = [
            {"text": "IRS", "url": "https://irs.gov"}
        ]
        mock_page.external_links = mock_extractor.extract_from_page.return_value

        mock_context = {"object_list": [mock_page]}

        with patch(
            "wagtail.admin.views.generic.base.BaseListingView.get_context_data",
            return_value=mock_context,
        ):
            with patch.object(view, "get_extractor", return_value=mock_extractor):
                context = view.get_context_data()

        assert isinstance(context["object_list"], list)

    def test_export_rows_returns_flat_list(self):
        view = self._make_view()
        page1 = MagicMock()
        page1.title = "Page 1"
        page1.slug = "page-1"
        page1.external_links = [
            {"text": "Link A", "url": "https://a.com"},
            {"text": "Link B", "url": "https://b.com"},
        ]
        page2 = MagicMock()
        page2.title = "Page 2"
        page2.slug = "page-2"
        page2.external_links = []

        rows = view.export_rows([page1, page2])
        assert len(rows) == 2
        assert rows[0]["title"] == "Page 1"
        assert rows[0]["link_url"] == "https://a.com"
        assert rows[1]["link_text"] == "Link B"

    def test_export_rows_empty_list(self):
        view = self._make_view()
        rows = view.export_rows([])
        assert rows == []
