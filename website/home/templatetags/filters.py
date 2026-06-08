from django import template
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.text import slugify

register = template.Library()


@register.filter
def column_width(column_count):
    return 12 // column_count


@register.filter
def get_type(value):
    """
    Return the type name of a value.
    Usage: {{ some_value|get_type }}
    """
    return type(value).__name__


@register.filter
def parse_iso_date(date_string):
    """
    Parse an ISO date string (from revision content) back to a datetime object
    """
    if not date_string:
        return None

    if isinstance(date_string, str):
        try:
            parsed_date = parse_datetime(date_string)
            if parsed_date:
                # Ensure the datetime is timezone-aware
                if timezone.is_naive(parsed_date):
                    parsed_date = timezone.make_aware(parsed_date)
                return parsed_date
        except (ValueError, TypeError):
            pass

    return date_string


@register.filter
def slugify_text(text):
    """
    Convert text to a URL-friendly slug
    """
    return slugify(text)


@register.filter
def aria_text(value):
    """
    Flatten a rich-text fragment into a single screen-reader-friendly string.

    Insert ", " before each closing </li>, </p>, </h1-6>, </br>, </div> tag so
    list items / paragraphs are spoken as separate phrases instead of running
    together. Then strip remaining HTML tags.

    Intended for use in ARIA labels.
    """
    if not value:
        return ""
    import re
    from django.utils.html import strip_tags

    s = str(value)
    # Insert separators before block-level closing tags
    s = re.sub(
        r"</(li|p|h[1-6]|br|div)>",
        r"</\1>, ",
        s,
        flags=re.IGNORECASE,
    )
    text = strip_tags(s)
    # Collapse runs of whitespace + trailing punctuation noise
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(,\s*)+", ", ", text)
    return text.rstrip(", ")
