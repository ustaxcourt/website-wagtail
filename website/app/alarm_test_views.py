"""Views for intentionally generating alarm-producing requests in non-production environments."""

import logging

from django.conf import settings
from django.db import connection, DatabaseError
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    return bool(getattr(settings, "ENABLE_ERROR_TEST_PAGES", False))


def alarm_test_index(request):
    if not _is_enabled():
        return HttpResponse("Not found", status=404)

    html = """
    <html>
      <head><title>Alarm Test Endpoints</title></head>
      <body>
        <h1>Alarm Test Endpoints</h1>
        <p>These routes intentionally generate log/error events for alarm testing.</p>
        <ul>
          <li><a href=\"/alarm-test/trigger-5xx/\">Trigger 5xx application error</a></li>
          <li><a href=\"/alarm-test/trigger-404/\">Trigger 404 page-not-found event</a></li>
          <li><a href=\"/alarm-test/trigger-rds-error/\">Trigger RDS SQL error event</a></li>
        </ul>
      </body>
    </html>
    """
    return HttpResponse(html)


def trigger_5xx(request):
    if not _is_enabled():
        return HttpResponse("Not found", status=404)

    # Emit two 500-shaped log records so a single hit can cross the >1 threshold.
    for _ in range(2):
        logger.error(
            "Intentional 5xx alarm test metric log.",
            extra={"status_code": 500, "path": request.path},
        )

    logger.error("Intentional 5xx alarm test endpoint hit.")
    raise RuntimeError("Intentional 5xx alarm test exception")


def trigger_404(request):
    if not _is_enabled():
        return HttpResponse("Not found", status=404)

    # Emit 51 entries so one hit can cross the >50 404 threshold.
    for _ in range(51):
        logger.warning(
            "Intentional 404 alarm test metric log.",
            extra={"status_code": 404, "path": request.path},
        )

    logger.warning("Intentional 404 alarm test endpoint hit.")
    return HttpResponse("Intentional 404 alarm test", status=404)


def trigger_rds_error(request):
    if not _is_enabled():
        return HttpResponse("Not found", status=404)

    try:
        # Intentionally invalid SQL to force a database error that will surface in DB logs.
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alarm_test_missing_table")
    except DatabaseError:
        logger.exception("Intentional RDS alarm test endpoint hit.")
        raise

    return HttpResponse("Unexpected success", status=500)
