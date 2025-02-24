from django import template

register = template.Library()


@register.filter
def strip_trailing_slash(value):
    if value.endswith("/"):
        return value[:-1]
    return value


@register.filter
def column_width(column_count):
    return 12 // column_count
