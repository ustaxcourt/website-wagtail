import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from home.utils.secrets import get_secret_from_aws

User = get_user_model()

SUPERUSERS_LIST_SECRET_KEY = "SUPERUSERS_TO_PREREGISTER"


class Command(BaseCommand):
    help = "Pre-registers superusers from a secret containing a list of emails."

    def get_superusers_from_configured_secret(self):
        """
        Retrieves the superuser list using the provided get_secret utility.
        """
        self.stdout.write(
            f"Attempting to retrieve superuser list using secret key: '{SUPERUSERS_LIST_SECRET_KEY}'"
        )
        try:
            superusers_data_or_json_string = get_secret_from_aws(
                SUPERUSERS_LIST_SECRET_KEY
            )

            if superusers_data_or_json_string is None:
                self.stderr.write(
                    self.style.ERROR(
                        f"Secret key '{SUPERUSERS_LIST_SECRET_KEY}' not found or utility returned None."
                    )
                )
                return None

            if isinstance(superusers_data_or_json_string, str):
                try:
                    superusers_data = json.loads(superusers_data_or_json_string)
                except json.JSONDecodeError as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Failed to parse JSON string for '{SUPERUSERS_LIST_SECRET_KEY}': {e}. "
                            f"Content was: '{superusers_data_or_json_string[:100]}...' (truncated)"
                        )
                    )
                    self.stderr.write(
                        self.style.WARNING(
                            "This might happen if your secrets utility generated a password "
                            "instead of providing a user list for this key."
                        )
                    )
                    return None
            elif isinstance(superusers_data_or_json_string, list):
                superusers_data = superusers_data_or_json_string
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f"Expected a list or JSON string for '{SUPERUSERS_LIST_SECRET_KEY}', "
                        f"but got type {type(superusers_data_or_json_string)}."
                    )
                )
                return None

            if not isinstance(superusers_data, list):
                self.stderr.write(
                    self.style.ERROR(
                        f"Data for '{SUPERUSERS_LIST_SECRET_KEY}' is not a list after processing. "
                        "Please ensure it's a list of email strings."
                    )
                )
                return None

            return superusers_data

        except RuntimeError as e:
            self.stderr.write(
                self.style.ERROR(f"Runtime error from secrets utility: {e}")
            )
            return None
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Unexpected error retrieving secret for '{SUPERUSERS_LIST_SECRET_KEY}': {e}"
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

        superusers_to_preregister = self.get_superusers_from_configured_secret()

        if superusers_to_preregister is None:
            self.stderr.write(
                self.style.ERROR(
                    "Failed to retrieve or parse superuser email data via secrets utility. Aborting."
                )
            )
            return

        if not superusers_to_preregister:
            self.stdout.write(
                self.style.SUCCESS(
                    "No superuser emails found in the list from secrets utility to pre-register."
                )
            )
            return

        for email_entry in superusers_to_preregister:
            if not isinstance(email_entry, str):
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping non-string item in superuser email list: {email_entry}"
                    )
                )
                continue

            email = email_entry.strip().lower()  # Ensure consistency in email
            if not email:
                self.stderr.write(self.style.ERROR("Skipping entry with empty email."))
                continue

            username = email

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
                            first_name="",  # Set to null, will be updated by SSO
                            last_name="",  # Set to null, will be updated by SSO
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

                # Ensure user is staff and superuser
                if not user.is_staff:
                    user.is_staff = True
                    update_needed = True
                if not user.is_superuser:
                    user.is_superuser = True
                    update_needed = True
                    self.stdout.write(f"Made {user.username} a superuser.")

                # Set first_name and last_name to null if they have values (SSO will update)
                if user.first_name != "" or user.last_name != "":
                    user.first_name = ""
                    user.last_name = ""
                    update_needed = True

                if update_needed:
                    self.stdout.write(f"Updating details for user {username}.")
                    user.save()
                else:
                    self.stdout.write(
                        f"User {username} is already a superuser with null first/last name. No update needed."
                    )
