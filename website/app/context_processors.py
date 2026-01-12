from django.conf import settings

from home.models.snippets.banners import Banner


def build_info(request):
    return {"build_sha": settings.GITHUB_SHA[:7]}


def _get_timezone_offset_ms():
    """
    Calculate the timezone offset in milliseconds from Django's timezone settings.
    This is used to adjust banner dates on the client side.

    Returns: Offset in milliseconds (e.g., 3600000 for UTC+1)
    """
    import pytz
    from django.utils import timezone

    # Get the configured timezone
    tz_name = settings.TIME_ZONE
    tz = pytz.timezone(tz_name)

    # Create a timezone-aware datetime and get its UTC offset
    now = timezone.now()
    offset = now.astimezone(tz).utcoffset()

    # Convert timedelta to milliseconds
    if offset:
        return int(offset.total_seconds() * 1000)
    return 0


def yellow_priority_news(request):
    """
    Context processor to provide yellow priority banners for display.
    Returns all live high priority banners without date filtering.
    Client-side JavaScript will handle date filtering and display logic.
    """
    import json

    yellow_banners = (
        Banner.objects.live()
        .filter(priority_level="high")
        .order_by("-banner_start_date")
    )

    # Serialize banners to JSON for client-side processing
    banners_data = []
    for item in yellow_banners:
        banners_data.append(
            {
                "id": item.id,
                "title": item.banner_title,
                "description": str(item.description),  # Convert RichText to HTML string
                "priority_level": item.priority_level,
                "document_url": item.document.url if item.document else None,
                "banner_start_date": item.banner_start_date.isoformat()
                if item.banner_start_date
                else None,
                "banner_end_date": item.banner_end_date.isoformat()
                if item.banner_end_date
                else None,
            }
        )

    return {
        "yellow_priority_news_json": json.dumps(banners_data),
        "has_yellow_news": len(banners_data) > 0,
        "timezone_offset_ms": _get_timezone_offset_ms(),
    }


def critical_priority_news(request):
    """
    Context processor to provide critical priority banners for red banner display.
    Returns all live critical priority banners without date filtering.
    Client-side JavaScript will handle date filtering and display logic.
    """
    import json

    critical_banners = (
        Banner.objects.live()
        .filter(priority_level="critical")
        .order_by("-banner_start_date")
    )

    # Serialize news items to JSON for client-side processing
    banners_data = []
    for item in critical_banners:
        banners_data.append(
            {
                "id": item.id,
                "title": item.banner_title,
                "description": str(item.description),  # Convert RichText to HTML string
                "priority_level": item.priority_level,
                "document_url": item.document.url if item.document else None,
                "banner_start_date": item.banner_start_date.isoformat()
                if item.banner_start_date
                else None,
                "banner_end_date": item.banner_end_date.isoformat()
                if item.banner_end_date
                else None,
            }
        )

    return {
        "critical_priority_news_json": json.dumps(banners_data),
        "has_critical_news": len(banners_data) > 0,
        "timezone_offset_ms": _get_timezone_offset_ms(),
    }
