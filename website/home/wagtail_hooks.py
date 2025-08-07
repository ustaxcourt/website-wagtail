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
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import Page
from home.models import NavigationMenu, JudgeRole
from home.models.snippets.judges import RESTRICTED_ROLES
from home.models.custom_blocks.add_entry_above_view import add_entry_above_view

from home.models.workflow import CustomWorkflowState
from home.models import CommonText
from home.models import EnhancedStandardPage
from home.models.snippets.judges import JudgeProfile, JudgeCollection
from home.models.snippets.navigation import NavigationRibbon
from wagtail.admin.ui.components import Component
from django.template.loader import render_to_string

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


# List all models using workflow with PublishDeadlineMixin
MONITORED_MODELS = [
    # Pages
    EnhancedStandardPage,
    # Snippets
    CommonText,
    JudgeProfile,
    JudgeCollection,
    JudgeRole,
    NavigationRibbon,
    NavigationMenu,
]


@receiver(post_save, sender=CustomWorkflowState)
def sync_deadline_from_content(sender, instance, created, **kwargs):
    """
    When a CustomWorkflowState is created, copy the publish_deadline/review_by_date
    from the related page or snippet into the workflow state object.
    """
    # Only on creation
    if not created:
        return

    # Get the actual content object
    content = None
    if instance.content_type and instance.object_id:
        model_class = instance.content_type.model_class()
        try:
            content = model_class.objects.get(pk=instance.object_id)
        except model_class.DoesNotExist:
            pass

    if not content:
        return

    # Only copy if fields exist on content
    deadline = getattr(content, "publish_deadline", None)
    review_by = getattr(content, "review_by_date", None)

    fields_to_update = []
    if hasattr(instance, "publish_deadline"):
        if deadline is not None:
            instance.publish_deadline = deadline
        else:
            # Set default deadline since field is now required (7 days from now)
            from django.utils import timezone
            from datetime import timedelta

            instance.publish_deadline = timezone.now() + timedelta(days=7)
        fields_to_update.append("publish_deadline")

    if hasattr(instance, "review_by_date"):
        if review_by is not None:
            instance.review_by_date = review_by
        else:
            # Set default review date since field is now required (3 days from now)
            from django.utils import timezone
            from datetime import timedelta

            instance.review_by_date = timezone.now() + timedelta(days=3)
        fields_to_update.append("review_by_date")

    if fields_to_update:
        instance.save(update_fields=fields_to_update)
        logger.info(
            f"CustomWorkflowState saved: {instance} - publish_deadline: {instance.publish_deadline}"
        )


# Signal receiver to create CustomWorkflowState when standard WorkflowState is created
@receiver(post_save, sender="wagtailcore.WorkflowState")
def create_custom_workflow_state(sender, instance, created, **kwargs):
    """
    When a standard WorkflowState is created, create a corresponding CustomWorkflowState
    with deadline information from the content object.
    """
    if not created:
        return

    # Check if CustomWorkflowState already exists for this workflow state
    try:
        CustomWorkflowState.objects.get(pk=instance.pk)
        return  # Already exists
    except CustomWorkflowState.DoesNotExist:
        pass

    # Get the content object
    content = None
    if instance.content_type and instance.object_id:
        model_class = instance.content_type.model_class()
        try:
            content = model_class.objects.get(pk=instance.object_id)
        except model_class.DoesNotExist:
            pass

    # Get deadline from content if available
    deadline = None
    if content and hasattr(content, "publish_deadline"):
        deadline = content.publish_deadline

    # Set default deadline if none provided (since field is now required)
    if deadline is None:
        from django.utils import timezone
        from datetime import timedelta

        deadline = timezone.now() + timedelta(days=7)

    # Create CustomWorkflowState record
    try:
        custom_state = CustomWorkflowState(
            workflowstate_ptr_id=instance.pk,
            publish_deadline=deadline,
            review_by_date=timezone.now() + timedelta(days=3),  # Default review date
        )
        custom_state.__dict__.update(instance.__dict__)
        custom_state.save()

        logger.info(
            f"Created CustomWorkflowState for {instance} with deadline: {deadline}"
        )
    except Exception as e:
        logger.error(f"Error creating CustomWorkflowState for {instance}: {e}")


class CustomAwaitingReviewPanel(Component):
    name = "custom_pages_for_moderation"
    title = "Awaiting your review"
    order = 100

    @property
    def media(self):
        from django import forms

        return forms.Media()

    def get_workflow_tasks(self, user):
        """
        Get all workflow tasks (both pages and snippets) awaiting review.
        """
        from home.models.workflow import CustomWorkflowState

        # Get all workflow states that are in progress
        workflow_states = (
            CustomWorkflowState.objects.filter(
                status=CustomWorkflowState.STATUS_IN_PROGRESS
            )
            .select_related("content_type", "workflow")
            .prefetch_related("current_task_state")
        )

        # Build list of workflow tasks for the template
        workflow_tasks = []
        for state in workflow_states:
            if state.current_task_state:
                # Create a task object similar to what the page workflow uses
                task_info = {
                    "workflow_state": state,
                    "task": state.current_task_state,
                    "is_snippet": state.content_type.model_class() != Page,
                }
                workflow_tasks.append(task_info)

        return workflow_tasks

    def get_context_data(self, parent_context=None):
        context = super().get_context_data(parent_context)

        # Get request from parent_context if available
        if parent_context and "request" in parent_context:
            request = parent_context["request"]
        else:
            # If no request in context, we can't get user-specific data
            context["workflow_tasks"] = []
            return context

        # Get all workflow tasks (pages and snippets)
        workflow_tasks = self.get_workflow_tasks(request.user)
        context["workflow_tasks"] = workflow_tasks

        return context

    def render_html(self, parent_context=None):
        context = self.get_context_data(parent_context)
        return render_to_string(
            "wagtailadmin/home/workflow_objects_to_moderate.html", context
        )


@hooks.register("construct_homepage_panels")
def replace_awaiting_review_panel(request, panels):
    # Find the index of the default pages_for_moderation panel
    index = next(
        (i for i, panel in enumerate(panels) if panel.name == "pages_for_moderation"),
        None,
    )

    # If found, replace it with your custom panel
    if index is not None:
        panels[index] = CustomAwaitingReviewPanel()
    else:
        panels.append(CustomAwaitingReviewPanel())
