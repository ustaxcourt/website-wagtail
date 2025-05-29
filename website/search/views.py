from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.utils.html import strip_tags

from wagtail.models import Page
from wagtail.blocks import StreamValue

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and the lines indicated in the search function
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

# from wagtail.contrib.search_promotions.models import Query


def extract_text_from_streamfield(stream_value, max_length=300):
    """
    Recursively extract text from a StreamField value.
    """
    if not stream_value:
        return ""
    text = []
    for block in stream_value:
        value = block.value
        if hasattr(value, "stream_data") or hasattr(
            value, "blocks"
        ):  # Nested StreamBlock
            text.append(extract_text_from_streamfield(value, max_length))
        elif hasattr(value, "source"):  # RichTextBlock
            text.append(str(value.source))
        elif isinstance(value, str):
            text.append(value)
        elif isinstance(value, dict):
            for v in value.values():
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

        # Handle StreamValue directly
        if isinstance(body, StreamValue):
            return extract_text_from_streamfield(body)
        # Handle other cases
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
        # Add search snippets to results
        for result in search_results:
            result.search_snippet = get_search_snippet(result)

    else:
        search_results = Page.objects.none()

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
        },
    )
