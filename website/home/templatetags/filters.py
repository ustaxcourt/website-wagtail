from django import template
from django.utils.dateparse import parse_datetime
from django.utils import timezone

register = template.Library()


@register.filter
def column_width(column_count):
    return 12 // column_count


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
def has_card_tiles(stream_blocks):
    """
    Check if any block in the StreamField has block_type 'card_tiles'
    Returns True if found, False otherwise
    """
    if not stream_blocks:
        return False

    for block in stream_blocks:
        if hasattr(block, "block_type") and block.block_type == "card_tiles":
            return True

    return False
