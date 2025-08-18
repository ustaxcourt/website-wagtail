from django import template
import re

register = template.Library()

DEADLINE_RE = re.compile(r"(?<!\w)(DEADLINE FOR FILING:)")
IMPORTANT_RE = re.compile(r"\s*(IMPORTANT:)")


@register.filter
def highlight_labels(value: str) -> str:
    if not isinstance(value, str):
        return value
    value = DEADLINE_RE.sub(
        r'<strong class="callout-label">\1</strong>', value, count=1
    )
    value = IMPORTANT_RE.sub(
        r'<br>&nbsp;<strong class="callout-label">\1</strong>', value, count=1
    )
    return value
