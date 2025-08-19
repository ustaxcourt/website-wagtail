from django import template
import re

register = template.Library()

DEADLINE_RE = re.compile(r"(?<!\w)(DEADLINE FOR FILING:)")
TIME_PHRASE_RE = re.compile(r"11:59\s*p\.m\.,\s*Eastern time,", re.IGNORECASE)
DAWSON_BREAK_RE = re.compile(r"(\bdue\.)\s+(DAWSON has been designed\b)")


@register.filter
def highlight_labels(value: str) -> str:
    if not isinstance(value, str):
        return value
    value = TIME_PHRASE_RE.sub(r"<strong>\g<0></strong>", value, count=1)
    value = DEADLINE_RE.sub(
        r'<strong class="callout-label">\1</strong>', value, count=1
    )
    value = DAWSON_BREAK_RE.sub(r"\1<br>\2", value, count=1)
    return value
