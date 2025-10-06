from django.conf import settings
from home.models.snippets.news_item import NewsItem


def build_info(request):
    return {"build_sha": settings.GITHUB_SHA[:7]}


def yellow_priority_news(request):
    """
    Context processor to provide yellow priority news items for banner display.
    Returns all live high priority news items without date filtering.
    Client-side JavaScript will handle date filtering and display logic.
    """
    import json

    yellow_news_items = (
        NewsItem.objects.live().filter(banner_options="high").order_by("-publish_date")
    )

    # Serialize news items to JSON for client-side processing
    news_data = []
    for item in yellow_news_items:
        news_data.append(
            {
                "id": item.id,
                "description": str(item.description),  # Convert RichText to HTML string
                "banner_start_date": item.banner_start_date.isoformat()
                if item.banner_start_date
                else None,
                "banner_end_date": item.banner_end_date.isoformat()
                if item.banner_end_date
                else None,
                "document_url": item.document.url if item.document else None,
            }
        )

    return {
        "yellow_priority_news_json": json.dumps(news_data),
        "has_yellow_news": len(news_data) > 0,
    }
