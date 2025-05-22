# myapp/management/commands/preregister_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model # Use get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from home.utils.secrets import get_secret

User = get_user_model() # Get the currently active User model

# Define the name of your secret in AWS Secrets Manager
# It's good practice to fetch this from settings or an environment variable
# For example, in your settings.py: AWS_PREREGISTER_USERS_SECRET_NAME = 'myapp/preregistered_users'
AWS_SECRET_NAME = "USERS_TO_PREREGISTER"
# getattr(settings, 'AWS_PREREGISTER_USERS_SECRET_NAME', 'myapp/default_preregister_secret_name')
# AWS_REGION_NAME = getattr(settings, 'AWS_SECRETS_MANAGER_REGION', 'us-east-1') # Or your desired region

class Command(BaseCommand):
    help = 'Pre-registers users from AWS Secrets Manager and assigns them to Wagtail/Django groups.'


    def handle(self, *args, **options):
        if not getattr(settings, 'SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL', False):
            self.stdout.write(self.style.WARNING(
                "Warning: SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL is not set to True. "
                "This script assumes username is the full email."
            ))

        users_to_preregister = get_secret(AWS_SECRET_NAME)

        if users_to_preregister is None:
            self.stderr.write(self.style.ERROR("Failed to retrieve or parse user data from Secrets Manager. Aborting."))
            return

        if not users_to_preregister:
            self.stdout.write(self.style.SUCCESS("No users found in the Secrets Manager list to pre-register."))
            return


        for user_data in users_to_preregister:
            email = user_data.get('email', '').strip()
            if not email:
                self.stderr.write(self.style.ERROR("Skipping entry with empty email."))
                continue

            username = email
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            role_names = user_data.get('role_names', [])

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
                self.stdout.write(f"User with email {email} not found. Attempting to find by username '{username}'.")
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
                        # Use create_user from the User model's manager
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name
                        )
                        user.set_unusable_password() # SSO will handle auth
                        # user.is_active = True # create_user usually sets this by default
                        self.stdout.write(self.style.SUCCESS(f"Successfully created user: {username}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error creating user {username}: {e}"))
                        continue
            except User.MultipleObjectsReturned:
                self.stderr.write(self.style.ERROR(
                    f"Multiple users found with email {email}. This should not happen. Please clean up duplicates manually."
                ))
                continue
            except Exception as e:
                 self.stderr.write(self.style.ERROR(f"An unexpected error occurred looking for user {email}: {e}"))
                 continue

            if user:
                update_needed = False
                if user.first_name != first_name:
                    user.first_name = first_name
                    update_needed = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    update_needed = True
                if not user.is_staff: # All Wagtail admin users need is_staff
                    user.is_staff = True # Set is_staff to True for Wagtail admin access
                    update_needed = True

                if update_needed:
                    self.stdout.write(f"Updating details for user {username}.")

                self.assign_groups(user, role_names)
                user.save()

    def assign_groups(self, user, role_names):
        current_group_names = set(user.groups.values_list('name', flat=True))
        target_group_names = set(role_names)

        # Add user to groups they are not yet in
        groups_to_add = target_group_names - current_group_names
        for role_name in groups_to_add:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
                self.stdout.write(f"Added user {user.username} to group {role_name}")
            except Group.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Group '{role_name}' does not exist. Please create it first."))
