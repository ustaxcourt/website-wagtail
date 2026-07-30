"""Tests for search/dawson_client.py — the DAWSON public API client."""

from datetime import datetime, timezone
import requests
from unittest.mock import MagicMock, patch

from search.dawson_client import get_case_record


CASE_RESPONSE = {
    "entityName": "PublicCaseDTO",
    "docketNumber": "5695-23",
    "docketNumberWithSuffix": "5695-23",
    "caseCaption": "Beyonce Knowles-Carter, Petitioner",
    # Deliberately different from the Petition entry's filingDate below, so
    # tests can confirm the Petition entry takes precedence.
    "receivedAt": "2023-04-18T10:00:00.000Z",
    "docketEntries": [
        {
            "documentType": "Request for Place of Trial",
            "filingDate": "2023-04-17T23:33:48.093Z",
        },
        {
            "documentType": "Petition",
            "filingDate": "2023-04-17T23:33:48.093Z",
        },
    ],
}


class TestGetCaseRecord:
    def test_successful_lookup_returns_case_record(self):
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.return_value = CASE_RESPONSE
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            record = get_case_record("5695-23")

        assert record is not None
        assert record.docket_number == "5695-23"
        assert record.case_caption == "Beyonce Knowles-Carter, Petitioner"
        assert record.dawson_url.endswith("/case-detail/5695-23")

    def test_filing_date_uses_petition_entry_over_case_level_received_at(self):
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.return_value = CASE_RESPONSE
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            record = get_case_record("5695-23")

        # The Petition docket entry is the document that actually opens the
        # case, so its filingDate is used rather than the case-level
        # receivedAt field, whose semantics aren't documented by the API.
        assert record.filing_date == datetime(
            2023, 4, 17, 23, 33, 48, 93000, tzinfo=timezone.utc
        )

    def test_filing_date_falls_back_to_received_at_without_petition_entry(self):
        data = {**CASE_RESPONSE, "docketEntries": []}
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.return_value = data
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            record = get_case_record("5695-23")

        assert record.filing_date == datetime(
            2023, 4, 18, 10, 0, 0, tzinfo=timezone.utc
        )

    def test_not_found_returns_none(self):
        mock_response = MagicMock(status_code=404, ok=False)
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            assert get_case_record("99999-99") is None

    def test_server_error_returns_none(self):
        mock_response = MagicMock(status_code=500, ok=False)
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            assert get_case_record("5695-23") is None

    def test_request_exception_returns_none(self):
        with patch(
            "search.dawson_client.requests.get",
            side_effect=requests.Timeout("timed out"),
        ):
            assert get_case_record("5695-23") is None

    def test_non_json_response_returns_none(self):
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.side_effect = ValueError("not json")
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            assert get_case_record("5695-23") is None

    def test_response_missing_expected_fields_returns_none(self):
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.return_value = {"entityName": "PublicCaseDTO"}
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            assert get_case_record("5695-23") is None

    def test_unparseable_filing_date_falls_back_to_none(self):
        data = {**CASE_RESPONSE, "receivedAt": "not-a-date", "docketEntries": []}
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.return_value = data
        with patch("search.dawson_client.requests.get", return_value=mock_response):
            record = get_case_record("5695-23")
        assert record is not None
        assert record.filing_date is None

    def test_requests_get_called_with_docket_number_in_url(self):
        mock_response = MagicMock(status_code=200, ok=True)
        mock_response.json.return_value = CASE_RESPONSE
        with patch(
            "search.dawson_client.requests.get", return_value=mock_response
        ) as mock_get:
            get_case_record("5695-23")
            called_url = mock_get.call_args[0][0]
            assert called_url.endswith("/cases/5695-23")
