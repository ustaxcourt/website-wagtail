import logging
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DAWSON_API_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class DawsonCaseRecord:
    """A case record returned by the DAWSON public API, trimmed to what the
    search result UI needs (docket record title, docket number, filing date,
    and a link to the full record in DAWSON)."""

    docket_number: str
    case_caption: str
    filing_date: datetime | None
    dawson_url: str


def _parse_filing_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_environment_specific_dawson_url(prefix=None):
    if settings.ENVIRONMENT == "production":
        url = "dawson.ustaxcourt.gov"
    elif settings.ENVIRONMENT == "train":
        url = "test.ef-cms.ustaxcourt.gov"
    else:  # Default to development [local, dev, sandbox, all others]
        url = "dev.ef-cms.ustaxcourt.gov"
    if prefix:
        return f"https://{prefix}.{url}"
    return f"https://{url}"


def get_case_record(docket_number: str) -> DawsonCaseRecord | None:
    """
    Look up a case record in DAWSON by docket number.

    Returns None if DAWSON has no record for this docket number, or if the
    request fails for any reason. Per the AC, DAWSON API errors (and
    not-found results) should degrade to a "no results found" state for the
    caller rather than raising.
    """
    # docket_number is already constrained to digits/dashes/letters by
    # is_docket_number()'s regex before reaching this public helper, but
    # quote() guards this URL construction against path/query injection
    # if get_case_record() is ever called with less-trusted input.
    url = f"{get_environment_specific_dawson_url('public-api')}/public-api/cases/{quote(docket_number, safe='')}"
    try:
        response = requests.get(url, timeout=DAWSON_API_TIMEOUT_SECONDS)
    except requests.RequestException:
        logger.warning(
            "DAWSON API request failed for docket number %s",
            docket_number,
            exc_info=True,
        )
        return None

    if response.status_code == 404:
        return None

    if not response.ok:
        logger.warning(
            "DAWSON API returned HTTP %s for docket number %s",
            response.status_code,
            docket_number,
        )
        return None

    try:
        data = response.json()
    except ValueError:
        logger.warning(
            "DAWSON API returned a non-JSON response for docket number %s",
            docket_number,
        )
        return None

    return _parse_case_record(data)


def _find_petition_filing_date(data: dict) -> str | None:
    """
    The case's filing date is the filingDate of its Petition docket entry —
    the document that actually opens the case — rather than the case-level
    receivedAt field, whose semantics aren't documented by the API.
    """
    for entry in data.get("docketEntries") or []:
        if entry.get("documentType") == "Petition":
            return entry.get("filingDate")
    return None


def _parse_case_record(data: dict) -> DawsonCaseRecord | None:
    docket_number = data.get("docketNumberWithSuffix") or data.get("docketNumber")

    if data.get("isSealed"):
        # A sealed case is treated as though the docket number doesn't
        # exist — no case details are shown. DAWSON's response for a sealed
        # case (entityName "RestrictedCaseDTO") also omits caseCaption, so
        # this would degrade to None below regardless, but checking
        # isSealed directly makes the intent explicit rather than relying
        # on that as an incidental side effect.
        return None

    case_caption = data.get("caseCaption")
    if not docket_number or not case_caption:
        # Log field presence, not the payload itself — it can contain
        # litigant PII (petitioner/practitioner names) that shouldn't be
        # written into application logs.
        logger.warning(
            "DAWSON API response missing expected fields "
            "(has_docket_number=%s, has_case_caption=%s), keys=%s",
            bool(docket_number),
            bool(case_caption),
            sorted(data.keys()),
        )
        return None

    filing_date_raw = _find_petition_filing_date(data) or data.get("receivedAt")

    return DawsonCaseRecord(
        docket_number=docket_number,
        case_caption=case_caption,
        filing_date=_parse_filing_date(filing_date_raw),
        dawson_url=f"{get_environment_specific_dawson_url()}/case-detail/{docket_number}",
    )
