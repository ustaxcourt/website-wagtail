from wagtail import hooks
from django.contrib import messages
from .models import NavigationMenu, JudgeRole
from django.shortcuts import redirect
from django.urls import reverse


@hooks.register("before_delete_snippet")
def prevent_navigation_menu_deletion(request, instances):
    # Prevent deletion of NavigationMenu instances
    if any(isinstance(instance, NavigationMenu) for instance in instances):
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
                messages.error(
                    request,
                    "You cannot delete the role 'Chief Judge' or 'Chief Special Trial Judge' as they are required for site functionality.",
                )
                referer = request.META.get("HTTP_REFERER")
                if referer:
                    return redirect(referer)
                return redirect(reverse("wagtailsnippets:index"))
