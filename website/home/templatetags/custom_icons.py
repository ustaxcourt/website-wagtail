from django import template

register = template.Library()


@register.filter
def custom_icons(value):
    icon_map = {
        "::pdf": "<i class='ti ti-file-type-pdf'></i>",
        "::info": "<i class='ti ti-info-circle-filled'></i>",
        "::indent": "&nbsp;&nbsp;&nbsp;&nbsp;",
    }
    for icon, icon_html in icon_map.items():
        value = value.replace(icon, icon_html)
    return value
