import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from home.utils.secrets import get_secret_from_aws  # Assuming this utility exists

User = get_user_model()

USERS_ROLES_SECRET_KEY = "USERS_TO_PREREGISTER"


class Command(BaseCommand):
    help = "Pre-registers users from secrets and assigns them to Django groups based on roles. If roles are assigned, superuser status will be removed."

    def get_users_with_roles_from_secret(self):
        """
        Retrieves the user list with roles using the provided get_secret utility.
        Expected format: { "RoleName1": ["email1@example.com", "email2@example.com"], "RoleName2": [...] }
        """
        self.stdout.write(
            f"Attempting to retrieve user roles using secret key: '{USERS_ROLES_SECRET_KEY}'"
        )
        try:
            users_data_or_json_string = get_secret_from_aws(USERS_ROLES_SECRET_KEY)

            if users_data_or_json_string is None:
                self.stderr.write(
                    self.style.ERROR(
                        f"Secret key '{USERS_ROLES_SECRET_KEY}' not found or utility returned None."
                    )
                )
                return None

            if isinstance(users_data_or_json_string, str):
                try:
                    users_data = json.loads(users_data_or_json_string)
                except json.JSONDecodeError as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Failed to parse JSON string for '{USERS_ROLES_SECRET_KEY}': {e}. "
                            f"Content was: '{users_data_or_json_string[:100]}...' (truncated)"
                        )
                    )
                    self.stderr.write(
                        self.style.WARNING(
                            "This might happen if your secrets utility generated a password "
                            "instead of providing a user list for this key."
                        )
                    )
                    return None
            elif isinstance(users_data_or_json_string, dict):
                users_data = users_data_or_json_string
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f"Expected a dictionary or JSON string for '{USERS_ROLES_SECRET_KEY}', "
                        f"but got type {type(users_data_or_json_string)}."
                    )
                )
                return None

            if not isinstance(users_data, dict):
                self.stderr.write(
                    self.style.ERROR(
                        f"Data for '{USERS_ROLES_SECRET_KEY}' is not a dictionary after processing. "
                        "Please ensure it's a mapping of role names to email lists."
                    )
                )
                return None

            return users_data

        except RuntimeError as e:  # Assuming get_secret_from_aws might raise this
            self.stderr.write(
                self.style.ERROR(f"Runtime error from secrets utility: {e}")
            )
            return None
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Unexpected error retrieving secret for '{USERS_ROLES_SECRET_KEY}': {e}"
                )
            )
            return None

    def handle(self, *args, **options):
        if not getattr(settings, "SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL", False):
            self.stdout.write(
                self.style.WARNING(
                    "Warning: SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL is not set to True. "
                    "This script assumes username is the full email."
                )
            )

        users_roles_data = self.get_users_with_roles_from_secret()

        if users_roles_data is None:
            self.stderr.write(
                self.style.ERROR(
                    "Failed to retrieve or parse user role data via secrets utility. Aborting."
                )
            )
            return

        if not users_roles_data:
            self.stdout.write(
                self.style.SUCCESS(
                    "No user roles found in the list from secrets utility to pre-register."
                )
            )
            return

        consolidated_users = {}
        for role_name, emails in users_roles_data.items():
            if not isinstance(role_name, str) or not role_name.strip():
                self.stderr.write(
                    self.style.WARNING(f"Skipping invalid role name: {role_name}")
                )
                continue
            if not isinstance(emails, list):
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping role '{role_name}' as its value is not a list of emails."
                    )
                )
                continue

            for email_entry in emails:
                if not isinstance(email_entry, str):
                    self.stderr.write(
                        self.style.WARNING(
                            f"Skipping non-string item in email list for role '{role_name}': {email_entry}"
                        )
                    )
                    continue

                email = email_entry.strip().lower()
                if not email:
                    self.stderr.write(
                        self.style.ERROR(  # Changed to ERROR as an empty email is problematic
                            f"Skipping empty email entry found for role '{role_name}'."
                        )
                    )
                    continue

                if email not in consolidated_users:
                    consolidated_users[email] = {"roles": set()}
                consolidated_users[email]["roles"].add(role_name.strip())

        for email, user_data in consolidated_users.items():
            username = email
            roles_for_user = list(user_data["roles"])

            user = None
            try:
                user = User.objects.get(email__iexact=email)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found existing user by email: {email} (Username: {user.username})"
                    )
                )

                if (
                    user.username != username
                ):  # Username is email, so this means username needs update
                    self.stdout.write(
                        self.style.WARNING(
                            f"User {email} found, but username '{user.username}' is not email. "
                            f"Attempting to update username to '{username}'."
                        )
                    )
                    # Check for username collision before updating
                    if (
                        User.objects.filter(username__iexact=username)
                        .exclude(pk=user.pk)
                        .exists()
                    ):
                        self.stderr.write(
                            self.style.ERROR(
                                f"Cannot update username for {email} to '{username}' because another user already has that username. Please resolve manually."
                            )
                        )
                        continue  # Skip this user
                    else:
                        user.username = username
                        # user.save() will be called later if update_needed

            except User.DoesNotExist:
                try:
                    # Attempt to find by username if SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL might not be strictly followed or for legacy data
                    user = User.objects.get(username__iexact=username)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Found existing user by username: {username}"
                        )
                    )
                    # If found by username, ensure email matches or update it
                    if user.email.lower() != email.lower():
                        self.stdout.write(
                            self.style.WARNING(
                                f"User {username} found, but email '{user.email}' differs from target '{email}'. Updating email."
                            )
                        )
                        user.email = email
                        # user.save() will be called later if update_needed
                except User.DoesNotExist:
                    self.stdout.write(
                        f"User {username} (email: {email}) does not exist. Creating new user."
                    )
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name="",
                            last_name="",
                        )
                        user.set_unusable_password()  # Good practice for SSO managed users
                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully created user: {username}")
                        )
                        # No need to set update_needed here as save is part of create_user
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(f"Error creating user {username}: {e}")
                        )
                        continue  # Skip this user
            except User.MultipleObjectsReturned:
                self.stderr.write(
                    self.style.ERROR(
                        f"Multiple users found with email {email}. Please clean up duplicates manually."
                    )
                )
                continue  # Skip this user
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"An unexpected error occurred looking for user {email}: {e}"
                    )
                )
                continue  # Skip this user

            if user:
                update_needed = False

                # Ensure first_name and last_name are blank (or null if your model allows)
                if user.first_name != "":
                    user.first_name = ""
                    update_needed = True
                if user.last_name != "":
                    user.last_name = ""
                    update_needed = True

                # If roles are specified for this user:
                if roles_for_user:
                    # Ensure is_staff is True if there are roles assigned
                    if not user.is_staff:
                        user.is_staff = True
                        update_needed = True
                        self.stdout.write(
                            f"Set is_staff=True for user {user.username} as roles are assigned."
                        )

                    # **NEW LOGIC: Remove superuser status if roles are assigned**
                    if user.is_superuser:
                        user.is_superuser = False
                        update_needed = True
                        self.stdout.write(
                            self.style.WARNING(
                                f"User {user.username} was a superuser. Removing superuser status as roles ({', '.join(roles_for_user)}) are being assigned by this script."
                            )
                        )
                else:  # No roles specified in the secret for this user
                    # If no roles are specified, we won't touch is_staff or is_superuser.
                    # If the requirement was to also remove is_staff if no roles, add logic here.
                    if user.is_superuser:
                        self.stdout.write(
                            self.style.NOTICE(  # Using NOTICE as it's not a warning in this case
                                f"User {user.username} is a superuser and no roles are specified for them in the secret. Superuser status remains unchanged by this script."
                            )
                        )
                    if (
                        user.is_staff
                        and not user.groups.exists()
                        and not user.is_superuser
                    ):  # Only if they have no other reason to be staff
                        self.stdout.write(
                            self.style.NOTICE(
                                f"User {user.username} is staff but has no roles assigned by this script and is not a superuser. is_staff status remains unchanged."
                            )
                        )

                if update_needed:
                    try:
                        user.save()
                        self.stdout.write(
                            f"Successfully updated details for user {user.username}."
                        )
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f"Error saving updates for user {user.username}: {e}"
                            )
                        )
                        continue  # Skip group assignment if save failed

                self.assign_groups(user, roles_for_user)

    def assign_groups(self, user, role_names):
        """
        Assigns user to specified groups (roles) and removes from groups not in the list.
        """
        if not isinstance(
            role_names, list
        ):  # Should be a list from the processing logic
            self.stderr.write(
                self.style.ERROR(
                    f"Internal error: role_names is not a list for user {user.username}"
                )
            )
            return

        current_group_names = set(user.groups.values_list("name", flat=True))
        target_group_names = set(role_names)

        # If no roles are specified for the user in the secret,
        # we explicitly remove them from any groups that might have been defined by this script previously.
        # However, we should only remove groups that *this script manages*.
        # For now, this script assumes any group name found in users_roles_data is "managed" by it.
        # A more robust solution might involve tagging groups or having a predefined list of manageable groups.

        groups_to_add = target_group_names - current_group_names
        groups_to_remove = (
            current_group_names - target_group_names
        )  # Remove groups user is in, but are not in target roles

        for role_name in groups_to_add:
            try:
                group, created = Group.objects.get_or_create(name=role_name)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created group '{role_name}' as it did not exist."
                        )
                    )
                user.groups.add(group)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added user {user.username} to group '{role_name}'"
                    )
                )
            except Exception as e:  # Catch broader exceptions for group operations
                self.stderr.write(
                    self.style.ERROR(
                        f"Error adding user {user.username} to group '{role_name}': {e}"
                    )
                )

        for role_name in groups_to_remove:
            # Only remove groups that *could* have been assigned by this script.
            # This assumes all role_names encountered in the secret are fair game.
            try:
                group = Group.objects.get(name=role_name)
                user.groups.remove(group)
                self.stdout.write(
                    f"Removed user {user.username} from group '{role_name}' as it's no longer in their specified roles."
                )
            except Group.DoesNotExist:
                # This should not happen if the group was in current_group_names, but good to log.
                self.stderr.write(
                    self.style.WARNING(  # Warning as it's an unexpected state but not critical for the current operation
                        f"Attempted to remove user {user.username} from non-existent group '{role_name}'. It might have been deleted manually."
                    )
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Error removing user {user.username} from group '{role_name}': {e}"
                    )
                )
