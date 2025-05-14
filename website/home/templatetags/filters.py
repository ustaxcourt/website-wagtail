from django import template

register = template.Library()


@register.filter
def column_width(column_count):
    return 12 // column_count
