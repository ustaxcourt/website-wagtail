import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from home.utils.secrets import get_secret_from_aws

User = get_user_model()

USERS_ROLES_SECRET_KEY = (
    "USERS_TO_PREREGISTER"  # Renamed for clarity with the new structure
)


class Command(BaseCommand):
    help = "Pre-registers users from secrets and assigns them to Django groups based on roles."

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

        except RuntimeError as e:
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

        # Consolidate all users by email, and collect their roles
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
                        self.style.ERROR(
                            f"Skipping empty email entry found for role '{role_name}'."
                        )
                    )
                    continue

                if email not in consolidated_users:
                    consolidated_users[email] = {"roles": set()}
                consolidated_users[email]["roles"].add(role_name.strip())

        for email, user_data in consolidated_users.items():
            username = email
            roles_for_user = list(
                user_data["roles"]
            )  # Convert set to list for consistent iteration

            user = None
            try:
                user = User.objects.get(email__iexact=email)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found existing user by email: {email} (Username: {user.username})"
                    )
                )

                if user.username != username:
                    self.stdout.write(
                        self.style.WARNING(
                            f"User {email} found, but username '{user.username}' is not email. "
                            f"Attempting to update username to '{username}'."
                        )
                    )
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
                        continue
                    else:
                        user.username = username

            except User.DoesNotExist:
                try:
                    user = User.objects.get(username__iexact=username)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Found existing user by username: {username}"
                        )
                    )
                    if user.email.lower() != email.lower():
                        self.stdout.write(
                            self.style.WARNING(
                                f"User {username} found, but email '{user.email}' differs from target '{email}'. Updating email."
                            )
                        )
                        user.email = email
                except User.DoesNotExist:
                    self.stdout.write(
                        f"User {username} (email: {email}) does not exist. Creating new user."
                    )
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name="",  # Set to null for SSO
                            last_name="",  # Set to null for SSO
                        )
                        user.set_unusable_password()
                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully created user: {username}")
                        )
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(f"Error creating user {username}: {e}")
                        )
                        continue
            except User.MultipleObjectsReturned:
                self.stderr.write(
                    self.style.ERROR(
                        f"Multiple users found with email {email}. Please clean up duplicates manually."
                    )
                )
                continue
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"An unexpected error occurred looking for user {email}: {e}"
                    )
                )
                continue

            if user:
                update_needed = False

                # Ensure first_name and last_name are null if they have values (SSO will update)
                if user.first_name != "" or user.last_name != "":
                    user.first_name = ""
                    user.last_name = ""
                    update_needed = True

                # Ensure is_staff is True if there are roles assigned
                if roles_for_user and not user.is_staff:
                    user.is_staff = True
                    update_needed = True

                # Ensure is_superuser is False (unless manually set elsewhere)
                # The script won't unset is_superuser if it's already True.
                # If you need to explicitly demote, that would require more logic.
                if user.is_superuser:
                    self.stdout.write(
                        self.style.WARNING(
                            f"User {user.username} is a superuser. This script will not alter their superuser status."
                        )
                    )

                if update_needed:
                    self.stdout.write(f"Updating details for user {username}.")
                    user.save()

                self.assign_groups(user, roles_for_user)

    def assign_groups(self, user, role_names):
        current_group_names = set(user.groups.values_list("name", flat=True))
        target_group_names = set(role_names)

        groups_to_add = target_group_names - current_group_names
        groups_to_remove = (
            current_group_names - target_group_names
        )  # Remove groups not in the target list

        for role_name in groups_to_add:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
                self.stdout.write(f"Added user {user.username} to group {role_name}")
            except Group.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"Group '{role_name}' does not exist. Please create it first."
                    )
                )

        for role_name in groups_to_remove:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.remove(group)
                self.stdout.write(
                    f"Removed user {user.username} from group {role_name}"
                )
            except Group.DoesNotExist:
                # This should ideally not happen if it was in current_group_names, but as a safeguard:
                self.stderr.write(
                    self.style.ERROR(
                        f"Attempted to remove non-existent group '{role_name}' from user {user.username}."
                    )
                )
