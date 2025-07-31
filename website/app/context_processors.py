from django.conf import settings
from wagtail.models import TaskState


def build_info(request):
    return {"build_sha": settings.GITHUB_SHA[:7]}


def moderation_data(request):
    """Provide moderation workflow data for the admin interface."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    # Get pages pending the current user's review
    pending_reviews = (
        TaskState.objects.reviewable_by(request.user)
        .select_related(
            "revision",
            "revision__user",
            "workflow_state",
            "workflow_state__workflow",
            "task",
        )
        .prefetch_related(
            "revision__content_object",
            "revision__content_object__latest_revision",
        )
        .order_by("-started_at")[:10]
    )  # Limit to 10 most recent

    # Build moderation data with required fields
    moderation_items = []
    for task_state in pending_reviews:
        content_object = task_state.revision.content_object
        workflow_state = task_state.workflow_state

        # Determine URL patterns based on content type
        if (
            hasattr(content_object, "_meta")
            and content_object._meta.model_name == "page"
        ):
            workflow_action_url_name = "wagtailadmin_pages:workflow_action"
            workflow_preview_url_name = "wagtailadmin_pages:workflow_preview"
        else:
            # For snippets, we'll need to determine the viewset
            workflow_action_url_name = None
            workflow_preview_url_name = None

        # Get available actions for this task
        actions = (
            task_state.task.get_actions(content_object, request.user)
            if task_state.task
            else []
        )

        moderation_items.append(
            {
                "content_object": content_object,
                "title": getattr(content_object, "title", str(content_object)),
                "revision": task_state.revision,
                "task_state": task_state,
                "workflow_state": workflow_state,
                "actions": actions,
                "requested_by": workflow_state.requested_by,
                "requested_at": workflow_state.created_at,
                "workflow_action_url_name": workflow_action_url_name,
                "workflow_preview_url_name": workflow_preview_url_name,
            }
        )

    return {
        "pending_moderation_items": moderation_items,
    }
