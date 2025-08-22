from django.dispatch import receiver
from wagtail.signals import workflow_cancelled, workflow_approved
from home.mixins.moderation import ModerationMixin


@receiver(workflow_cancelled)
def clear_review_by_on_workflow_cancelled(sender, **kwargs):
    """Clear review_by date when workflow is cancelled."""
    instance = kwargs.get("instance")
    if instance and isinstance(instance, ModerationMixin):
        if hasattr(instance, "review_by") and instance.review_by:
            instance.review_by = None
            instance.save(update_fields=["review_by"])


@receiver(workflow_approved)
def clear_review_by_on_workflow_approved(sender, **kwargs):
    """Clear review_by date when workflow is approved."""
    instance = kwargs.get("instance")
    if instance and isinstance(instance, ModerationMixin):
        if hasattr(instance, "review_by") and instance.review_by:
            instance.review_by = None
            instance.save(update_fields=["review_by"])
