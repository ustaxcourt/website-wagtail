import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from home.utils.secrets import get_secret_from_aws

User = get_user_model()

# Define the key name used within your secrets utility to fetch the user list.
# This should be a key within the 'website_secrets' JSON (local or AWS).
# Fetch this from Django settings for better configurability.
USERS_LIST_SECRET_KEY = "USERS_TO_PREREGISTER"

class Command(BaseCommand):
    help = 'Pre-registers users from secrets (via utility) and assigns them to Wagtail/Django groups.'

    def get_users_from_configured_secret(self):
        """
        Retrieves the user list using the provided get_secret utility.
        """
        self.stdout.write(f"Attempting to retrieve user list using secret key: '{USERS_LIST_SECRET_KEY}'")
        try:
            # This 'users_data' is expected to be the list of user dictionaries,
            # or a JSON string representation of it.
            users_data_or_json_string = get_secret_from_aws(USERS_LIST_SECRET_KEY)

            if users_data_or_json_string is None:
                self.stderr.write(self.style.ERROR(
                    f"Secret key '{USERS_LIST_SECRET_KEY}' not found or utility returned None."
                ))
                return None

            if isinstance(users_data_or_json_string, str):
                # If it's a string, try to parse it as JSON.
                # This handles the case where the secret value is stored as a JSON string.
                try:
                    users_data = json.loads(users_data_or_json_string)
                except json.JSONDecodeError as e:
                    self.stderr.write(self.style.ERROR(
                        f"Failed to parse JSON string for '{USERS_LIST_SECRET_KEY}': {e}. "
                        f"Content was: '{users_data_or_json_string[:100]}...' (truncated)"
                    ))
                    self.stderr.write(self.style.WARNING(
                        "This might happen if your secrets utility generated a password "
                        "instead of providing a user list for this key."
                    ))
                    return None
            elif isinstance(users_data_or_json_string, list):
                users_data = users_data_or_json_string # It's already a list
            else:
                self.stderr.write(self.style.ERROR(
                    f"Expected a list or JSON string for '{USERS_LIST_SECRET_KEY}', "
                    f"but got type {type(users_data_or_json_string)}."
                ))
                return None

            if not isinstance(users_data, list):
                self.stderr.write(self.style.ERROR(
                     f"Data for '{USERS_LIST_SECRET_KEY}' is not a list after processing. "
                     "Please ensure it's a list of user objects."
                ))
                return None

            return users_data

        except RuntimeError as e: # Catching RuntimeError from your utility
            self.stderr.write(self.style.ERROR(f"Runtime error from secrets utility: {e}"))
            return None
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error retrieving secret for '{USERS_LIST_SECRET_KEY}': {e}"))
            return None


    def handle(self, *args, **options):
        if not getattr(settings, 'SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL', False):
            self.stdout.write(self.style.WARNING(
                "Warning: SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL is not set to True. "
                "This script assumes username is the full email."
            ))

        users_to_preregister = self.get_users_from_configured_secret()

        if users_to_preregister is None:
            self.stderr.write(self.style.ERROR(
                "Failed to retrieve or parse user data via secrets utility. Aborting."
            ))
            return

        if not users_to_preregister:
            self.stdout.write(self.style.SUCCESS(
                "No users found in the list from secrets utility to pre-register."
            ))
            return

        for user_data in users_to_preregister:
            if not isinstance(user_data, dict):
                self.stderr.write(self.style.WARNING(f"Skipping non-dictionary item in user list: {user_data}"))
                continue

            email = user_data.get('email', '').strip()
            if not email:
                self.stderr.write(self.style.ERROR("Skipping entry with empty email."))
                continue

            username = email
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            role_names = user_data.get('role_names', [])

            make_superuser = False
            for role_name in role_names:
                if role_name.lower() == 'admin':
                    make_superuser = True
                    self.stdout.write(self.style.SUCCESS(f"User {email} flagged as superuser ('Admin' role found)."))

            final_role_names_for_groups = [r for r in role_names if r.lower() != 'admin']

            user = None
            try:
                user = User.objects.get(email__iexact=email)
                self.stdout.write(self.style.SUCCESS(f"Found existing user by email: {email} (Username: {user.username})"))

                if user.username != username:
                    self.stdout.write(self.style.WARNING(
                        f"User {email} found, but username '{user.username}' is not email. "
                        f"Attempting to update username to '{username}'."
                    ))
                    if User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
                        self.stderr.write(self.style.ERROR(
                            f"Cannot update username for {email} to '{username}' because another user already has that username. Please resolve manually."
                        ))
                        continue
                    else:
                        user.username = username

            except User.DoesNotExist:
                try:
                    user = User.objects.get(username__iexact=username)
                    self.stdout.write(self.style.SUCCESS(f"Found existing user by username: {username}"))
                    if user.email.lower() != email.lower():
                         self.stdout.write(self.style.WARNING(
                            f"User {username} found, but email '{user.email}' differs from target '{email}'. Updating email."
                        ))
                         user.email = email
                except User.DoesNotExist:
                    self.stdout.write(f"User {username} (email: {email}) does not exist. Creating new user.")
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name
                        )
                        user.set_unusable_password()
                        self.stdout.write(self.style.SUCCESS(f"Successfully created user: {username}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error creating user {username}: {e}"))
                        continue
            except User.MultipleObjectsReturned:
                self.stderr.write(self.style.ERROR(
                    f"Multiple users found with email {email}. Please clean up duplicates manually."
                ))
                continue
            except Exception as e:
                 self.stderr.write(self.style.ERROR(f"An unexpected error occurred looking for user {email}: {e}"))
                 continue

            if user:
                update_needed = False
                if user.first_name != first_name or user.last_name != last_name or not user.is_staff:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_staff = True
                    update_needed = True

                if make_superuser:
                    if not user.is_superuser:
                        user.is_superuser = True
                        update_needed = True
                        self.stdout.write(f"Made {user.username} a superuser.")
                    if not user.is_staff:
                        user.is_staff = True
                        update_needed = True

                elif not user.is_staff: 
                    if final_role_names_for_groups:
                        user.is_staff = True
                        update_needed = True

                if update_needed:
                    self.stdout.write(f"Updating details for user {username}.")

                self.assign_groups(user, role_names)
                user.save()

    def assign_groups(self, user, role_names):
        current_group_names = set(user.groups.values_list('name', flat=True))
        target_group_names = set(role_names)

        groups_to_add = target_group_names - current_group_names
        for role_name in groups_to_add.filter(group__iexact="admin"):
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
                self.stdout.write(f"Added user {user.username} to group {role_name}")
            except Group.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Group '{role_name}' does not exist. Please create it first."))
