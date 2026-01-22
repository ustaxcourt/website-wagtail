from django import template
from django.utils.safestring import mark_safe

import re

register = template.Library()


@register.filter
def phone_link(phone_number):
    """
    Converts a phone number into a clickable 'tel:' link.
    Strips characters like (), -, and spaces.
    """
    if phone_number:
        stripped_number = re.sub(r"[()\-\s]", "", phone_number)
        return f'<a href="tel:{stripped_number}" title="call: {phone_number}">{phone_number}</a>'
    return phone_number


@register.filter
def judge_display_name(judge):
    if judge.roles.exists():
        role = judge.roles.first()
        return f"{role.role_name} {judge.display_name}"
    return f"{judge.title} {judge.display_name}"


@register.filter
def clean_filename(filename):
    """Remove extension and replace - and _ with spaces."""
    if "." in filename:
        filename = filename.rsplit(".", 1)[0]
    return filename.replace("-", " ").replace("_", " ")


@register.filter
def get_type(value):
    """
    Returns the type name of a value for debugging in templates.
    Usage: {{ some_value|get_type }}
    """
    return type(value).__name__


@register.simple_tag
def include_svg(document):
    """
    Renders the content of an SVG document inline.
    """
    if document and document.file.name.lower().endswith(".svg"):
        try:
            document.file.open("r")
            svg_content = document.file.read()
            document.file.close()
            return mark_safe(svg_content)
        except IOError:
            pass

    return ""
