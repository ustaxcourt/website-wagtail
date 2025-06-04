from wagtail import hooks
from django.contrib import messages
from .models import NavigationMenu, JudgeRole
from .common_models.judges import RESTRICTED_ROLES
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .utils.aws_cloudfront import invalidate_cloudfront_cache

import logging

logger = logging.getLogger(__name__)


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
                message_text = (
                    f"""You cannot delete the role "{'", "'.join(RESTRICTED_ROLES)}" as they are required for site functionality.""",
                )
                logger.info(message_text)
                messages.error(request, message_text)
                referer = request.META.get("HTTP_REFERER")
                if referer:
                    return redirect(referer)
                return redirect(reverse("wagtailsnippets:index"))


@hooks.register("after_edit_snippet")
def invalidate_cloudfront_on_snippet_edit(request, instance):
    """
    Invalidate CloudFront cache when a snippet is saved.
    """
    env = getattr(settings, "ENVIRONMENT", "dev")
    if env != "production":
        logger.debug(f"Skipping CloudFront invalidation in {env} environment.")
        return

    distribution_id = getattr(settings, "CLOUDFRONT_DISTRIBUTION_ID", None)
    if not distribution_id:
        logger.error("CLOUDFRONT_DISTRIBUTION_ID not set in settings.")
        return

    snippet_type = type(instance).__name__.lower()
    path_map = {
        "commontext": ["/"],
        "fancycard": ["/cards/*"],
        "judgecollection": ["/judges/*"],
        "judgeprofile": ["/judges/*"],
        "judgerole": ["/judges/*"],
        "navigationmenu": ["/nav/*"],
        "navigationribbon": ["/nav/*"],
        "simplecard": ["/cards/*"],
    }

    paths = path_map.get(snippet_type, ["/*"])

    try:
        invalidate_cloudfront_cache(distribution_id, paths)
        logger.info(f"Invalidated CloudFront cache for: {paths}")
    except Exception as e:
        logger.error(f"Failed to invalidate CloudFront for snippet: {e}")
