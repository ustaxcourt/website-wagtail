from wagtail import hooks
from django.contrib import messages
from .models import NavigationMenu, JudgeRole
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.admin.menu import MenuItem
import logging

logger = logging.getLogger(__name__)


@hooks.register(
    "register_settings_menu_item"
)  # Or 'register_admin_menu_item' for a top-level item
def register_role_switcher_menu_item():
    return MenuItem(
        _("Switch Role (Testing)"),
        reverse("switch_role"),
        icon_name="user",  # Choose an appropriate icon
        order=1000,  # Adjust order as needed
        classname="icon icon-user",  # Ensure icon_name matches if you use this
    )


@hooks.register("before_delete_snippet")
def prevent_navigation_menu_deletion(request, instances):
    # Prevent deletion of NavigationMenu instances
    if any(isinstance(instance, NavigationMenu) for instance in instances):
        logger.info(
            "Navigation Menus cannot be deleted as they are required for site functionality.",
        )
        messages.error(
            request,
            "Navigation Menus cannot be deleted as they are required for site functionality.",
        )
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied()


@hooks.register("before_delete_snippet")
def protect_special_judge_roles(request, snippets):
    for snippet in snippets:
        # Only proceed for JudgeRole snippets
        if isinstance(snippet, JudgeRole):
            if snippet.role_name in ["Chief Judge", "Chief Special Trial Judge"]:
                logger.info(
                    "You cannot delete the role 'Chief Judge' or 'Chief Special Trial Judge' as they are required for site functionality.",
                )
                messages.error(
                    request,
                    "You cannot delete the role 'Chief Judge' or 'Chief Special Trial Judge' as they are required for site functionality.",
                )
                referer = request.META.get("HTTP_REFERER")
                if referer:
                    return redirect(referer)
                return redirect(reverse("wagtailsnippets:index"))
