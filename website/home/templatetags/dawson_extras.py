from django import template
import re

register = template.Library()


@register.filter
def highlight_important(value: str) -> str:
    return re.sub(
        r"(?<!\w)(IMPORTANT:)", r'<strong class="important-label">\1</strong>', value
    )
