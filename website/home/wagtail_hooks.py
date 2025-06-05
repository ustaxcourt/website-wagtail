from django.contrib import messages
from django.conf import settings
from .models import NavigationMenu, JudgeRole
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
import logging

logger = logging.getLogger(__name__)

try:
    from app.role_switcher.views import (
        SESSION_IS_ASSUMING_ROLE_KEY,
        SESSION_ORIGINAL_IS_SUPERUSER_KEY,
    )
except ImportError:
    SESSION_IS_ASSUMING_ROLE_KEY = "is_assuming_role"
    SESSION_ORIGINAL_IS_SUPERUSER_KEY = "original_is_superuser"


def environment_is_prod():
    try:
        return settings.ENVIRONMENT == "production"
    except (AttributeError, KeyError):
        return False


class ConditionalRoleSwitcherMenuItem(MenuItem):
    """
    A custom menu item that is only shown if the user is a superuser,
    or was originally a superuser and is currently assuming another role.
    """

    def is_shown(self, request):
        # Condition 1: The user is currently a superuser (in their DB record)
        is_current_superuser = (
            request.user.is_authenticated and request.user.is_superuser
        )

        # Condition 2: Check session state for role switching
        is_assuming_role = request.session.get(SESSION_IS_ASSUMING_ROLE_KEY, False)
        was_originally_superuser = request.session.get(
            SESSION_ORIGINAL_IS_SUPERUSER_KEY, False
        )

        # The menu item should be shown if:
        # - Environment is not prod
        # - They are currently a superuser (and not in a switched state that originated from non-superuser)
        # - OR they are in a switched state that originated from a superuser account.
        if environment_is_prod():
            return False
        if is_assuming_role:
            result = was_originally_superuser  # Show if they started as a superuser
            return result
        else:
            # Not assuming a role, show only if they are currently a superuser
            result = is_current_superuser
            return result


@hooks.register("register_settings_menu_item")
def register_conditional_role_switcher_menu_item():
    return ConditionalRoleSwitcherMenuItem(
        _("Switch User Role for Testing"),
        reverse("switch_role"),
        icon_name="user",
        order=10000,
        classname="icon icon-user",
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
