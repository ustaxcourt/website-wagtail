from urllib.parse import urlparse
from django.contrib import messages
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.utils.safestring import mark_safe
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import Page
from home.models import NavigationMenu, JudgeRole
from home.models.snippets.judges import RESTRICTED_ROLES
from home.models.snippets.news_item import NewsItem
from home.models.custom_blocks.add_entry_above_view import add_entry_above_view
from datetime import timedelta

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


@hooks.register("before_edit_snippet")
def populate_news_item_expiration_date(request, instance):
    """
    Auto-populate homepage_display_expiration_date with publish_date + 7 days
    when editing a NewsItem, if expiration date is not already set.
    """
    if isinstance(instance, NewsItem):
        # Only populate if expiration date is not set and publish date exists
        if not instance.homepage_display_expiration_date and instance.publish_date:
            instance.homepage_display_expiration_date = (
                instance.publish_date + timedelta(days=7)
            )
            logger.info(
                f"Auto-populated expiration date for NewsItem '{instance.title}' to {instance.homepage_display_expiration_date}"
            )


@hooks.register("before_create_snippet")
def populate_new_news_item_expiration_date(request, model):
    """
    Auto-populate homepage_display_expiration_date with publish_date + 7 days
    when creating a new NewsItem, if expiration date is not set.
    """
    if model == NewsItem:
        # This hook runs before the form is displayed for creation
        # The actual population will be handled by JavaScript or form logic
        pass


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
    """
    try:
        from wagtail.contrib.frontend_cache.utils import PurgeBatch

        if file_url.startswith("http"):
            parsed = urlparse(file_url)
            cache_path = parsed.path
        else:
            cache_path = file_url if file_url.startswith("/") else f"/{file_url}"

        if cache_path.startswith("/files/"):
            cache_path = cache_path.removeprefix("/files")

        logger.debug(f"Purging CloudFront cache for path: {cache_path}")

        batch = PurgeBatch()
        batch.add_url(cache_path)
        batch.purge()

        logger.info(f"Successfully purged CloudFront cache for path: {cache_path}")

    except Exception as e:
        logger.error(
            f"Error purging CloudFront cache for {file_url}: {e}", exc_info=True
        )


@receiver(post_save, sender=Document)
def purge_cache_after_document_save(sender, instance, created, **kwargs):
    """
    Purge CloudFront cache when a document is saved (created or updated).
    """
    del sender, kwargs
    action = "created" if created else "updated"

    logger.info(f"Document {action}: {instance.title} (ID: {instance.id})")

    if hasattr(instance, "url") and instance.url and action == "updated":
        logger.debug(f"Document URL: {instance.url}")
        purge_cloudfront_cache_for_file(instance.url)
    elif action == "created":
        pass
    else:
        logger.warning(f"Document {instance.id} has no URL attribute or URL is empty")


@receiver(post_delete, sender=Document)
def purge_cache_after_document_delete(sender, instance, **kwargs):
    """
    Purge CloudFront cache when a document is deleted.
    """
    del sender, kwargs

    logger.info(f"Document deleted: {instance.title} (ID: {instance.id})")

    if hasattr(instance, "url") and instance.url:
        logger.info(f"Document URL: {instance.url}")
        purge_cloudfront_cache_for_file(instance.url)
    else:
        logger.warning(f"Document {instance.id} has no URL attribute or URL is empty")


@receiver(post_save, sender=Image)
def purge_cache_after_image_save(sender, instance, created, **kwargs):
    """
    Purge CloudFront cache when an image is saved (created or updated).
    """
    del sender, kwargs
    action = "created" if created else "updated"
    logger.info(f"Image {action}: {instance.title} (ID: {instance.id})")

    if hasattr(instance, "file") and instance.file:
        try:
            image_url = instance.file.url
            logger.info(f"Image URL: {image_url}")
            purge_cloudfront_cache_for_file(image_url)
        except Exception as e:
            logger.error(f"Error getting image URL for cache purge: {e}")
    else:
        logger.warning(f"Image {instance.id} has no file attribute or file is empty")


@receiver(post_delete, sender=Image)
def purge_cache_after_image_delete(sender, instance, **kwargs):
    """
    Purge CloudFront cache when an image is deleted.
    """
    del sender, kwargs
    logger.info(f"Image deleted: {instance.title} (ID: {instance.id})")

    if hasattr(instance, "file") and instance.file:
        try:
            image_url = instance.file.url
            logger.info(f"Image URL: {image_url}")
            purge_cloudfront_cache_for_file(image_url)
        except Exception as e:
            logger.error(f"Error getting image URL for cache purge: {e}")
    else:
        logger.warning(f"Image {instance.id} has no file attribute or file is empty")


@hooks.register("register_admin_urls")
def register_add_entry_above_url():
    return [
        path(
            "add_entry_above/<int:page_id>/<int:sort_order>/",
            add_entry_above_view,
            name="add_entry_above_view",
        ),
    ]


@hooks.register("insert_editor_js")
def news_item_auto_populate_js():
    """
    JavaScript to auto-populate homepage_display_expiration_date when publish_date changes
    in the NewsItem admin form.
    """
    return mark_safe("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Check if we're on a NewsItem form
        if (document.querySelector('input[name="title"]') &&
            document.querySelector('input[name="publish_date_0"]') &&
            document.querySelector('input[name="homepage_display_expiration_date_0"]')) {

            const publishDateField = document.querySelector('input[name="publish_date_0"]');
            const expirationDateField = document.querySelector('input[name="homepage_display_expiration_date_0"]');

            function updateExpirationDate() {
                const publishDate = publishDateField.value;
                if (publishDate && !expirationDateField.value) {
                    // Parse the date and add 7 days
                    const date = new Date(publishDate);
                    if (!isNaN(date.getTime())) {
                        date.setDate(date.getDate() + 7);

                        // Format as YYYY-MM-DD for the date input
                        const year = date.getFullYear();
                        const month = String(date.getMonth() + 1).padStart(2, '0');
                        const day = String(date.getDate()).padStart(2, '0');
                        const formattedDate = `${year}-${month}-${day}`;

                        expirationDateField.value = formattedDate;

                        // Trigger change event to ensure Wagtail recognizes the change
                        expirationDateField.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }

            // Listen for changes to the publish date field
            publishDateField.addEventListener('change', updateExpirationDate);
            publishDateField.addEventListener('blur', updateExpirationDate);

            // Also run on initial load in case publish date is already set
            updateExpirationDate();
        }
    });
    </script>
    """)
