from django import template

from wagtail.models import Site
from home.models import NavigationMenu, NavigationRibbon

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@register.simple_tag(takes_context=True)
def get_navigation_menu(context):
    isPreviewRender = hasattr(context.get("self"), "menu_items")
    if isPreviewRender:
        return context["self"]
    else:
        return NavigationMenu.objects.filter(live=True).first()


@register.simple_tag(takes_context=True)
def get_navigation_ribbon(context):
    isPreviewRender = hasattr(context.get("self"), "links")
    if isPreviewRender:
        return context["self"]
    else:
        return NavigationRibbon.objects.filter(
            name="Guidance for Self-Represented Petitioners Ribbon"
        ).first()
