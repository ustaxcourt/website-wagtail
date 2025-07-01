from django.contrib import messages
from django.conf import settings
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache
from wagtail.models import Page
from home.models import NavigationMenu, JudgeRole
from home.models.snippets.judges import RESTRICTED_ROLES
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import path, reverse
from home.models.custom_blocks.add_entry_above_view import add_entry_above_view

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
        "fancycard": ["/"],
        "judgecollection": ["/home/judges/"],
        "judgeprofile": ["/home/judges/"],
        "judgerole": ["/home/judges/"],
        "navigationmenu": ["/"],
        "navigationribbon": ["/"],
        "simplecard": ["/"],
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
            logger.error(f"Error purging cache for page {page.id}: {e}")


def purge_cloudfront_cache_for_file(file_url):
    """
    Purge CloudFront cache for a specific file URL.
    This handles both documents and images served via /files/ path.
    """
    try:
        from wagtail.contrib.frontend_cache.utils import PurgeBatch

        if not file_url:
            logger.warning("No file URL provided for cache purge")
            return

        batch = PurgeBatch()
        batch.add_url(file_url)
        batch.purge()
        logger.info(f"Purged CloudFront cache for file: {file_url}")
    except Exception as e:
        logger.error(f"Error purging CloudFront cache for {file_url}: {e}")


@hooks.register("after_edit_document")
def purge_cache_after_document_edit(request, document):
    """
    Purge CloudFront cache when a document is edited/updated.
    """
    if hasattr(document, "url") and document.url:
        purge_cloudfront_cache_for_file(document.url)


@hooks.register("after_delete_document")
def purge_cache_after_document_delete(request, instances):
    """
    Purge CloudFront cache when documents are deleted.
    """
    for document in instances:
        if hasattr(document, "url") and document.url:
            purge_cloudfront_cache_for_file(document.url)


@hooks.register("after_edit_image")
def purge_cache_after_image_edit(request, image):
    """
    Purge CloudFront cache when an image is edited/updated.
    """
    if hasattr(image, "file") and image.file:
        try:
            image_url = image.file.url
            purge_cloudfront_cache_for_file(image_url)
        except Exception as e:
            logger.error(f"Error getting image URL for cache purge: {e}")


@hooks.register("after_delete_image")
def purge_cache_after_image_delete(request, instances):
    """
    Purge CloudFront cache when images are deleted.
    """
    for image in instances:
        if hasattr(image, "file") and image.file:
            try:
                image_url = image.file.url
                purge_cloudfront_cache_for_file(image_url)
            except Exception as e:
                logger.error(f"Error getting image URL for cache purge: {e}")


@hooks.register("register_admin_urls")
def register_add_entry_above_url():
    return [
        path(
            "add_entry_above/<int:page_id>/<int:sort_order>/",
            add_entry_above_view,
            name="add_entry_above_view",
        ),
    ]
