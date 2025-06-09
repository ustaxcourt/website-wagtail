from django.contrib import messages
from django.conf import settings
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache
from wagtail.models import Page
from .models import NavigationMenu, JudgeRole
from .models.snippets.judges import RESTRICTED_ROLES
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
            if snippet.role_name in RESTRICTED_ROLES:
                message_text = f"""You cannot delete the role "{'", "'.join(RESTRICTED_ROLES)}" as they are required for site functionality."""
                logger.info(message_text)
                messages.error(request, message_text)
                referer = request.META.get("HTTP_REFERER")
                if referer:
                    return redirect(referer)
                return redirect(reverse("wagtailsnippets:index"))


@hooks.register("after_edit_snippet")
def purge_cache_for_snippet_related_pages(request, instance):
    """
    Purge frontend cache for pages that might be affected by this snippet.
    This uses a snippet type to path mapping and matches live pages based on path.
    """
    snippet_type = type(instance).__name__.lower()

    path_map = {
        "commontext": ["/"],
        "judgecollection": ["/judges/"],
        "judgeprofile": ["/judges/"],
        "judgerole": ["/judges/"],
    }

    affected_prefixes = path_map.get(snippet_type, ["/"])
    affected_pages = []
    for prefix in affected_prefixes:
        pages = Page.objects.live().filter(url_path__startswith=prefix)
        affected_pages.extend(pages)

    if not affected_pages:
        logger.info(f"No affected pages found for snippet type '{snippet_type}'")
        return

    for page in affected_pages:
        try:
            purge_page_from_cache(page)
            logger.info(f"Purged frontend cache for page: {page.url_path}")
        except Exception as e:
            logger.warning(f"Error purging cache for page {page.id}: {e}")
