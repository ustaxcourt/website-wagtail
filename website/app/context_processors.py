from django.conf import settings

# from home.models.snippets.news_item import NewsItem
from home.models.snippets.banners import Banner


def build_info(request):
    return {"build_sha": settings.GITHUB_SHA[:7]}


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
    }
