from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.utils.html import strip_tags

from wagtail.models import Page
from wagtail.blocks import StreamValue
from wagtail.contrib.search_promotions.models import Query, SearchPromotion

from home.models.snippets.judges import JudgeProfile
from django.db.models import Q

SEARCH_EXCLUSION_PAGES = ["Press Releases & News"]


def extract_text_from_streamfield(stream_value, max_length=300):
    """
    Recursively extract text from a StreamField value.
    """
    if not stream_value:
        return ""
    text = []
    for block in stream_value:
        value = block.value
        if block.block_type == "questionanswers":
            for qa in value:
                if isinstance(qa, dict):
                    if "question" in qa:
                        text.append(qa["question"])
                    if "answer" in qa:
                        if isinstance(qa["answer"], str):
                            text.append(qa["answer"])
                        elif (
                            isinstance(qa["answer"], dict)
                            and "rich_text" in qa["answer"]
                        ):
                            text.append(str(qa["answer"]["rich_text"].source))
                        elif hasattr(qa["answer"], "source"):
                            text.append(str(qa["answer"].source))
        elif hasattr(value, "stream_data") or hasattr(
            value, "blocks"
        ):  # Nested StreamBlock
            text.append(extract_text_from_streamfield(value, max_length))
        elif hasattr(value, "source"):  # RichTextBlock
            text.append(str(value.source))
        elif isinstance(value, str):
            text.append(value)
        elif isinstance(value, dict):
            for k, v in value.items():
                if (
                    hasattr(v, "stream_data")
                    or hasattr(v, "blocks")
                    or isinstance(v, list)
                ):
                    text.append(extract_text_from_streamfield(v, max_length))
                elif isinstance(v, str):
                    text.append(v)
        elif isinstance(value, list):
            text.append(extract_text_from_streamfield(value, max_length))
    combined = strip_tags(" ".join(text))
    return combined[:max_length]


def get_search_snippet(page):
    """
    Get a search snippet from a page's content.
    """

    # Try getting the specific version of the page
    specific_page = page.specific

    if hasattr(specific_page, "body"):
        body = getattr(specific_page, "body")

        if hasattr(specific_page, "release_entries"):
            return strip_tags(specific_page.release_entries)
        elif isinstance(body, StreamValue):
            return extract_text_from_streamfield(body)
        elif hasattr(body, "stream_data") or hasattr(body, "blocks"):
            return extract_text_from_streamfield(body)
        elif isinstance(body, str):
            return strip_tags(body)[:300]

    if hasattr(specific_page, "intro"):
        return strip_tags(getattr(specific_page, "intro"))[:300]
    return ""


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query)
        judge_results = JudgeProfile.objects.live().filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(display_name__icontains=search_query)
            | Q(bio__icontains=search_query)
            | Q(chambers_telephone__icontains=search_query)
        )
        query = Query.get(search_query)
        query.add_hit()

        # Get search promotions
        search_promotions = SearchPromotion.objects.filter(query=query).select_related(
            "page"
        )

        # Filter out excluded pages and add search snippets to page results
        # Also, prepare a set of promoted page IDs for efficient lookup
        promoted_page_ids = {p.page.id for p in search_promotions if p.page}

        filtered_search_results = []
        for result in search_results:
            if result.title not in SEARCH_EXCLUSION_PAGES:
                # Add search snippet
                result.search_snippet = get_search_snippet(result)
                filtered_search_results.append(result)
        search_results = filtered_search_results

        # Handle duplicate pages between promotions and organic results
        # Iterate through search promotions to update descriptions and mark duplicates
        for promotion in search_promotions:
            if promotion.page:  # Ensure it's a page promotion
                # Check if this promoted page also exists in the organic search results
                for organic_result in search_results:
                    if organic_result.pk == promotion.page.pk:
                        # If a duplicate is found, copy the organic result's snippet to the promotion's description
                        # and mark the organic result for removal.
                        if (
                            hasattr(organic_result, "search_snippet")
                            and organic_result.search_snippet
                        ):
                            promotion.description = organic_result.search_snippet
                        break

        # Remove duplicate pages from search_results that are already in search_promotions
        search_results = [
            result for result in search_results if result.pk not in promoted_page_ids
        ]

        # Convert judge results to a compatible format
        for judge in judge_results:
            # Create a mock page-like object for the judge
            judge_page = type(
                "JudgePage",
                (),
                {
                    "title": judge.display_name
                    or f"{judge.first_name} {judge.last_name}",
                    "search_snippet": f"Judge {judge.display_name or f'{judge.first_name} {judge.last_name}'}",
                    "url": f"/judges/{judge.id}/{judge.last_name.lower()}",
                },
            )
            search_results.append(judge_page)

    else:
        search_results = Page.objects.none()
        search_promotions = (
            SearchPromotion.objects.none()
        )  # Initialize even if no query

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "search_promotions": search_promotions,  # Pass promotions to the template
        },
    )
