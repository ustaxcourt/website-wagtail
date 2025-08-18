from django import template
import re

register = template.Library()


@register.filter
def highlight_labels(value: str) -> str:
    patterns = [
        r"(?<!\w)(DEADLINE FOR FILING:)",
        r"(?<!\w)(IMPORTANT:)",
    ]
    for pat in patterns:
        value = re.sub(pat, r'<strong class="callout-label">\1</strong>', value)
    return value
