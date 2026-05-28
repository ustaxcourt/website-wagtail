"""Tests for home/models/pages/vacancy_announcements.py"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError


class TestVacancyAnnouncementsPageGetContext:
    def test_get_context_returns_active_vacancies(self):
        from home.models.pages.vacancy_announcements import VacancyAnnouncementsPage

        page = VacancyAnnouncementsPage.__new__(VacancyAnnouncementsPage)
        mock_qs = MagicMock()

        with (
            patch(
                "home.models.pages.vacancy_announcements.StandardPage.get_context",
                return_value={},
            ),
            patch(
                "home.models.pages.vacancy_announcements.VacancyEntry.objects.filter",
                return_value=mock_qs,
            ),
        ):
            mock_qs.order_by.return_value = mock_qs
            result = VacancyAnnouncementsPage.get_context(page, MagicMock())

        assert result["active_vacancies"] == mock_qs


class TestVacancyEntryClean:
    def _make_entry(self, closing_date=None, url=None, attachment=None):
        from home.models.pages.vacancy_announcements import VacancyEntry

        entry = MagicMock(spec=VacancyEntry)
        entry.closing_date = closing_date
        entry.url = url
        entry.attachment = attachment
        return entry

    def test_raises_if_closing_date_in_past(self):
        from home.models.pages.vacancy_announcements import VacancyEntry

        entry = self._make_entry(
            closing_date=date.today() - timedelta(days=1),
            url="http://example.com",
        )
        with pytest.raises(ValidationError, match="closing_date"):
            with patch("home.models.pages.vacancy_announcements.Orderable.clean"):
                VacancyEntry.clean(entry)

    def test_raises_if_no_url_and_no_attachment(self):
        from home.models.pages.vacancy_announcements import VacancyEntry

        entry = self._make_entry(
            closing_date=date.today() + timedelta(days=5),
            url=None,
            attachment=None,
        )
        with pytest.raises(ValidationError):
            with patch("home.models.pages.vacancy_announcements.Orderable.clean"):
                VacancyEntry.clean(entry)

    def test_no_error_with_url_and_future_date(self):
        from home.models.pages.vacancy_announcements import VacancyEntry

        entry = self._make_entry(
            closing_date=date.today() + timedelta(days=5),
            url="http://example.com",
        )
        with patch("home.models.pages.vacancy_announcements.Orderable.clean"):
            VacancyEntry.clean(entry)  # Should not raise


class TestVacancyEntryIsActive:
    def test_is_active_returns_true_for_future(self):
        from home.models.pages.vacancy_announcements import VacancyEntry

        entry = MagicMock(spec=VacancyEntry)
        entry.closing_date = date.today() + timedelta(days=1)
        assert VacancyEntry.is_active(entry) is True

    def test_is_active_returns_false_for_past(self):
        from home.models.pages.vacancy_announcements import VacancyEntry

        entry = MagicMock(spec=VacancyEntry)
        entry.closing_date = date.today() - timedelta(days=1)
        assert VacancyEntry.is_active(entry) is False
