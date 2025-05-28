from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import logging  # For better logging

# Import session keys from your views.py or a central constants file
# Assuming they are accessible from your views.py (role_switcher_view_py_v3)
from .views import (
    SESSION_ORIGINAL_GROUPS_KEY,
    SESSION_ORIGINAL_IS_SUPERUSER_KEY,
    SESSION_ORIGINAL_IS_STAFF_KEY,
    SESSION_IS_ASSUMING_ROLE_KEY,
    SESSION_ASSUMED_ROLE_NAME_KEY,  # Not strictly for revert, but good to clear
)

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(user_logged_out)
def revert_role_on_logout(sender, request, user, **kwargs):
    """
    Checks if a user was assuming a role when they logged out.
    If so, and they were originally a superuser (as indicated by session data
    set by the role switching tool), revert their database record to their
    original permissions.
    """
    if (
        not user
    ):  # User might be None if logout is part of user deletion or anonymous logout
        return

    try:
        # Check session if the user was in an "assuming role" state
        # AND was originally a superuser when they initiated the switch.
        # request.session should still be available when this signal is dispatched.
        is_assuming_role = request.session.get(SESSION_IS_ASSUMING_ROLE_KEY, False)
        was_originally_superuser = request.session.get(
            SESSION_ORIGINAL_IS_SUPERUSER_KEY, False
        )

        if is_assuming_role and was_originally_superuser:
            # Fetch a fresh instance from DB to ensure we're modifying the correct object
            # The 'user' object passed to the signal is request.user
            user_to_revert = User.objects.get(pk=user.pk)

            original_groups_pks = request.session.get(SESSION_ORIGINAL_GROUPS_KEY, [])

            # Restore original superuser and staff status from session
            user_to_revert.is_superuser = request.session.get(
                SESSION_ORIGINAL_IS_SUPERUSER_KEY, False
            )
            user_to_revert.is_staff = request.session.get(
                SESSION_ORIGINAL_IS_STAFF_KEY, False
            )

            # Restore original groups
            user_to_revert.groups.clear()
            if original_groups_pks:
                original_groups = Group.objects.filter(pk__in=original_groups_pks)
                user_to_revert.groups.set(original_groups)

            user_to_revert.save()

            logger.info(
                f"User '{user_to_revert.username}' (ID: {user_to_revert.pk}) was automatically reverted from an assumed role upon logout."
            )

            # Clean up our specific session keys.
            # Django's logout view will call request.session.flush() anyway,
            # but this is good for explicit cleanup of our keys if needed.
            for key in [
                SESSION_ORIGINAL_GROUPS_KEY,
                SESSION_ORIGINAL_IS_SUPERUSER_KEY,
                SESSION_ORIGINAL_IS_STAFF_KEY,
                SESSION_IS_ASSUMING_ROLE_KEY,
                SESSION_ASSUMED_ROLE_NAME_KEY,
            ]:
                if key in request.session:
                    del request.session[key]

    except User.DoesNotExist:
        logger.error(
            f"User with PK {user.pk} not found during automatic role revert on logout."
        )
    except Exception as e:
        # Log any other errors during this process, but don't prevent logout
        logger.error(
            f"Error during automatic role revert for user '{user.username}' (ID: {user.pk}) on logout: {e}",
            exc_info=True,
        )
