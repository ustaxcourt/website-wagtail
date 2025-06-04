from wagtail import hooks
from django.contrib import messages
from .models import NavigationMenu, JudgeRole
from .models.snippets.judges import RESTRICTED_ROLES
from django.shortcuts import redirect
from django.urls import reverse
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
