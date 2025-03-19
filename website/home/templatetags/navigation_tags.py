from django import template

from wagtail.models import Site
from home.models import NavigationMenu

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@register.simple_tag
def get_navigation_menu():
    menu = NavigationMenu.objects.filter(live=True).first()
    if menu:
        print(f"Found menu: {menu.name}")
        print(f"Menu is live: {menu.live}")
        print(f"Menu items count: {len(menu.menu_items)}")
        for section in menu.menu_items:
            print(f"Section: {section.value['title']}")
            for sub_link in section.value["sub_links"]:
                print(f"  - Sublink: {sub_link['title']}")
    else:
        print("No live menu found")
        # Print all menus for debugging
        all_menus = NavigationMenu.objects.all()
        print(f"Total menus: {all_menus.count()}")
        for m in all_menus:
            print(f"Menu: {m.name} (live: {m.live})")
    return menu
