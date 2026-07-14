from urllib.parse import urlparse
from django.contrib import messages
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.mail import send_mail
from wagtail.admin.menu import MenuItem
from wagtail.contrib.frontend_cache.utils import purge_pages_from_cache, PurgeBatch
from wagtail.contrib.redirects.models import Redirect
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import Page
from home.models import NavigationMenu, JudgeRole, Header
from home.models.snippets.news_item import NewsItem
from home.models.snippets.judges import RESTRICTED_ROLES
from home.models.custom_blocks.add_entry_above_view import add_entry_above_view
from .views import (
    SearchDefinitionsReportView,
    SVG_CHOOSER_VIEWSET,
    PDF_CHOOSER_VIEWSET,
)

import logging

from home.views import NewsItemReportView, PrivateSeminarDisclosureReportView
from wagtail.admin.menu import AdminOnlyMenuItem

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


def purge_cloudflare_root():
    """
    Purge CloudFront cache for all pages using wildcard /* path.
    Used when content that appears on all pages is updated (e.g., header, navigation menu, high-priority news items).
    """
    try:
        batch = PurgeBatch()
        batch.add_url("/*")
        batch.purge()
        logger.info("Purged CloudFront cache for all pages using wildcard /*")
        return True
    except Exception as e:
        logger.error(f"Error purging CloudFront cache for all pages: {e}")
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


@hooks.register("insert_global_admin_js")
def global_admin_js():
    return format_html(
        '<script src="{}"></script><script src="{}"></script>',
        static("home/js/news_item_admin.js"),
        static("home/js/list_type_admin.js"),
    )


@hooks.register("insert_global_admin_css")
def hide_typed_table_caption():
    """
    Hide the built-in caption input from the TypedTableBlock admin editor.
    The Enhanced Table component provides its own Header and Caption fields
    at the StructBlock level, rendered above the table widget.
    """
    return format_html(
        "<style>.typed-table-block > [data-field-wrapper] {{ display: none !important; }}</style>"
    )


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
        "newsitem": ["/", "/home/news-and-announcements/"],
    }

    # Purge CloudFront cache for all pages using wildcard when navigation menu changes
    if snippet_type == "navigationmenu":
        purge_cloudflare_root()
        return

    affected_prefixes = path_map.get(snippet_type, ["/"])
    affected_pages = []
    for prefix in affected_prefixes:
        pages = Page.objects.live().filter(url_path__startswith=prefix)
        affected_pages.extend(pages)

    if not affected_pages:
        logger.info(f"No affected pages found for snippet type '{snippet_type}'")
        return

    try:
        purge_pages_from_cache(affected_pages)
        logger.info(f"Purged frontend cache for pages: {affected_pages}")
    except Exception as e:
        logger.error(f"Error purging cache for pages: {affected_pages}: {e}")


def purge_cloudfront_cache_for_file(file_url):
    """
    Purge CloudFront cache for a specific file URL.
    """
    try:
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
        return

    try:
        refresh_redirects_for_local_environments(cache_path)
    except Exception as e:
        logger.error(
            f"Error updating redirect in local environment for {cache_path} : {e}",
            exc_info=True,
        )


def refresh_redirects_for_local_environments(cache_path):
    # The local environment's Document URL path is /documents/{doc_id}/{file_name}.
    # Other environments' Document URL path is /files/documents/{file_name}.
    # Redirects that are created as part of home migration 0115 use the Document URL path for non-local environments.
    # The code in this if block updates the redirects to use the local environment Document URL path if run against a local environment.
    # This code will also update redirects for images or any other items that are transmitted via CloudFront in non-local environments.
    if settings.ENVIRONMENT == "local":
        logger.debug(f"Checking for redirect to update for {cache_path}")
        last_slash_index = cache_path.rfind("/")
        if last_slash_index != -1:
            file_name_to_find_in_redirect = cache_path[last_slash_index + 1 :]
            redirect_to_update = (
                Redirect.objects.filter(
                    redirect_link__iendswith=file_name_to_find_in_redirect
                )
                .order_by("id")
                .first()
            )
            if redirect_to_update is not None:
                logger.debug(
                    f"Updating redirect with redirect_link: {redirect_to_update.redirect_link} to {cache_path}"
                )
                redirect_to_update.redirect_link = cache_path
                redirect_to_update.save()
                logger.debug("Redirect updated")


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


def _purge_newsitem_affected_pages():
    """
    Purge CloudFront cache for pages affected by NewsItem changes.
    Targets the home page and news-and-announcements page rather than purging all pages.
    """
    affected_pages = list(
        Page.objects.live().filter(url_path__in=["/", "/home/news-and-announcements/"])
    )
    if affected_pages:
        try:
            purge_pages_from_cache(affected_pages)
            logger.info(f"Purged cache for NewsItem-affected pages: {affected_pages}")
        except Exception as e:
            logger.error(f"Error purging cache for NewsItem-affected pages: {e}")


@receiver(post_save, sender=NewsItem)
def purge_cache_after_newsitem_save(sender, instance, created, **kwargs):
    """
    Purge CloudFront cache for the home page and news-and-announcements page
    when a NewsItem is created or updated.
    """
    del sender, kwargs
    action = "created" if created else "updated"
    logger.info(f"NewsItem {action}: {instance.title} (ID: {instance.id})")
    _purge_newsitem_affected_pages()


@receiver(post_delete, sender=NewsItem)
def purge_cache_after_newsitem_delete(sender, instance, **kwargs):
    """
    Purge CloudFront cache for the home page and news-and-announcements page
    when a NewsItem is deleted.
    """
    del sender, kwargs
    logger.info(f"NewsItem deleted: {instance.title} (ID: {instance.id})")
    _purge_newsitem_affected_pages()


@receiver(post_save, sender=Header)
def purge_cache_after_header_save(sender, instance, created, **kwargs):
    """
    Purge CloudFront cache for all pages when the header settings are updated.
    Header appears on all pages, so we need to purge all pages.
    """
    del sender, kwargs

    action = "created" if created else "updated"
    logger.info(f"Header settings {action} (ID: {instance.id})")
    purge_cloudflare_root()


@hooks.register("register_admin_urls")
def register_add_entry_above_url():
    return [
        path(
            "add_entry_above/<int:page_id>/<int:sort_order>/",
            add_entry_above_view,
            name="add_entry_above_view",
        ),
    ]


@hooks.register("after_edit_page")
def notify_submitter_on_superseding_edit_of_draft_currently_in_moderation(
    request, page
):
    """
    Checks if a page edit supersedes a revision currently in moderation.
    If the editor is not the original submitter, send a notification.
    """

    # 1. Check if the page is in an active workflow
    if not page.workflow_in_progress:
        return

    # A page in moderation must have a revision that is the 'content_object' of the workflow state
    in_moderation_revision = page.current_workflow_state.revisions().latest(
        "created_at"
    )
    if not in_moderation_revision or not in_moderation_revision.user:
        return

    # 2. Get the original submitter and the current editor
    original_submitter = in_moderation_revision.user
    current_editor = request.user

    # 3. If they are the same person, do nothing
    if original_submitter == current_editor:
        return

    # 4. If they are different, send the email notification
    page_edit_url = request.build_absolute_uri(
        reverse("wagtailadmin_pages:edit", args=[page.id])
    )
    context = {
        "page": page,
        "editor": current_editor,
        "submitter": original_submitter,
        "page_edit_url": page_edit_url,
        "user": original_submitter,  # The 'user' is the recipient of the email
        "base_url": request.build_absolute_uri("/")[:-1],
    }

    html_content = render_to_string(
        "wagtailadmin/mail/superseded_revision.html", context
    )
    plain_text_content = strip_tags(html_content)

    send_mail(
        subject=f"'{page.get_admin_display_title()}' has been updated while in review",
        recipient_list=[original_submitter.email],
        message=plain_text_content,
        html_message=html_content,
    )


@hooks.register("register_reports_menu_item")
def register_unpublished_changes_report_menu_item():
    return AdminOnlyMenuItem(
        "News and Announcements Publish Report",
        reverse("news_and_announcements_report"),
        icon_name="clipboard-list",
        order=700,
    )


@hooks.register("register_admin_urls")
def register_news_and_announcements_report_url():
    return [
        path(
            "reports/news-and-announcements-report/",
            NewsItemReportView.as_view(),
            name="news_and_announcements_report",
        ),
        path(
            "reports/news-and-announcements-report/results/",
            NewsItemReportView.as_view(results_only=True),
            name="news_and_announcements_report_results",
        ),
    ]


@hooks.register("register_reports_menu_item")
def register_searched_definitions_report_menu_item():
    return AdminOnlyMenuItem(
        "Search Definitions Report",
        reverse("search_definitions_report"),
        icon_name="clipboard-list",
    )


@hooks.register("register_admin_urls")
def register_searched_definitions_report_url():
    return [
        path(
            "reports/search-definitions-report/",
            SearchDefinitionsReportView.as_view(),
            name="search_definitions_report",
        ),
        path(
            "reports/search-definitions-report/results/",
            SearchDefinitionsReportView.as_view(results_only=True),
            name="search_definitions_report_results",
        ),
    ]


@hooks.register("register_reports_menu_item")
def register_private_seminar_disclosure_report_menu_item():
    # MenuItem (not AdminOnlyMenuItem) — visible to Admins, Moderators, and Editors.
    return MenuItem(
        "Private Seminar Disclosures Report",
        reverse("private_seminar_disclosure_report"),
        icon_name="clipboard-list",
        order=720,
    )


@hooks.register("register_admin_urls")
def register_private_seminar_disclosure_report_urls():
    return [
        path(
            "reports/private-seminar-disclosures/",
            PrivateSeminarDisclosureReportView.as_view(),
            name="private_seminar_disclosure_report",
        ),
        path(
            "reports/private-seminar-disclosures/results/",
            PrivateSeminarDisclosureReportView.as_view(results_only=True),
            name="private_seminar_disclosure_report_results",
        ),
    ]


@hooks.register("register_admin_viewset")
def register_svg_viewset():
    return SVG_CHOOSER_VIEWSET


@hooks.register("register_admin_viewset")
def register_pdf_viewset():
    return PDF_CHOOSER_VIEWSET
