from django import template

from wagtail.models import Site, Revision, ContentType
from home.models import NavigationMenu

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@register.simple_tag(takes_context=True)
def get_navigation_menu(context):
    request = context["request"]
    is_preview = request.GET.get("preview") == "true"

    if is_preview:
        # Get the latest revision of any NavigationMenu
        latest_revision = (
            Revision.objects.filter(
                base_content_type=ContentType.objects.get_for_model(NavigationMenu),
                content_type=ContentType.objects.get_for_model(NavigationMenu),
            )
            .order_by("-created_at")
            .first()
        )

        menu = latest_revision.as_object() if latest_revision else None
    else:
        # Get only live menus
        menu = NavigationMenu.objects.filter(live=True).first()

    if menu:
        print(f"Found menu: {menu.name} (preview mode: {is_preview})")
        print(f"Menu is live: {menu.live}")
        print(f"Menu items count: {len(menu.menu_items)}")
        for section in menu.menu_items:
            print(f"Section: {section.value['title']}")
            for sub_link in section.value["sub_links"]:
                print(f"  - Sublink: {sub_link['title']}")
    else:
        print(f"No menu found (preview mode: {is_preview})")
        all_menus = NavigationMenu.objects.all()
        print(f"Total menus: {all_menus.count()}")
        for m in all_menus:
            print(f"Menu: {m.name} (live: {m.live})")
    return menu
