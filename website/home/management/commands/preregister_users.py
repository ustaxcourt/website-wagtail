# myapp/management/commands/preregister_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group # Or your custom User model
from django.conf import settings # To potentially check SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL

# ... (your USERS_TO_PREREGISTER list) ...
# Example:
USERS_TO_PREREGISTER = [
    {'email': 'Miriam.Miest-Moore.ctr@ustaxcourt.gov', 'first_name': 'Miriam', 'last_name': 'Miest-Moore', 'role_names': ['Editors']},
    # ... other users
]

class Command(BaseCommand):
    help = 'Pre-registers users and assigns them to Wagtail/Django groups, compatible with email as username.'

    def handle(self, *args, **options):
        # It's good practice to ensure this script aligns with the setting
        # though python-social-auth handles the SSO part, this script creates users.
        if not getattr(settings, 'SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL', False):
            self.stdout.write(self.style.WARNING(
                "Warning: SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL is not set to True. "
                "This script assumes username is the full email."
            ))

        for user_data in USERS_TO_PREREGISTER:
            email = user_data['email'].strip() # Ensure no leading/trailing whitespace
            if not email:
                self.stderr.write(self.style.ERROR("Skipping entry with empty email."))
                continue

            # Since SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True, username MUST be the email
            username = email
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            role_names = user_data.get('role_names', [])

            user = None
            try:
                # Primary way to find an existing user should now be by email,
                # as this is unique and what SSO will likely use to link.
                user = User.objects.get(email__iexact=email) # Case-insensitive email look
                self.stdout.write(self.style.SUCCESS(f"Found existing user by email: {email} (Username: {user.username})"))

                # Sanity check/fix: If user found by email, ensure their username is also the email
                if user.username != username:
                    self.stdout.write(self.style.WARNING(
                        f"User {email} found, but username '{user.username}' is not email. "
                        f"Attempting to update username to '{username}'."
                    ))
                    # Check if the target username (the email) is already taken by another user
                    if User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
                        self.stderr.write(self.style.ERROR(
                            f"Cannot update username for {email} to '{username}' because another user already has that username. Please resolve manually."
                        ))
                        # Skip role assignment for this user or handle as error
                        continue
                    else:
                        user.username = username
                        # user.save() # Save username change here or with role updates

            except User.DoesNotExist:
                self.stdout.write(f"User with email {email} not found. Attempting to find by potential username '{username}' (which should be the email).")
                try:
                    # Fallback: Check if user exists with the username (which should be the email)
                    # This handles cases where email might not have been unique before, but username was.
                    user = User.objects.get(username__iexact=username)
                    self.stdout.write(self.style.SUCCESS(f"Found existing user by username: {username}"))
                    # Ensure their email is also correct if found this way
                    if user.email.lower() != email.lower():
                         self.stdout.write(self.style.WARNING(
                            f"User {username} found, but email '{user.email}' differs from target '{email}'. "
                            f"Updating email."
                        ))
                         user.email = email # Standardize email
                         # user.save() # Save email change here or with role updates

                except User.DoesNotExist:
                    self.stdout.write(f"User {username} (email: {email}) does not exist. Creating new user.")
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name
                        )
                        user.set_unusable_password() # SSO will handle auth
                        self.stdout.write(self.style.SUCCESS(f"Successfully created user: {username}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error creating user {username}: {e}"))
                        continue # Skip to next user in list

            except User.MultipleObjectsReturned:
                self.stderr.write(self.style.ERROR(
                    f"Multiple users found with email {email}. This should not happen. Please clean up duplicates manually."
                ))
                continue # Skip to next user in list
            except Exception as e:
                 self.stderr.write(self.style.ERROR(f"An unexpected error occurred looking for user {email}: {e}"))
                 continue


            if user:
                # Update details if necessary (optional)
                update_needed = False
                if user.first_name != first_name:
                    user.first_name = first_name
                    update_needed = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    update_needed = True
                if not user.is_staff: # All Wagtail admin users need is_staff
                    user.is_staff = True
                    update_needed = True

                if update_needed:
                    self.stdout.write(f"Updating details for user {username}.")
                
                # Assign/update roles (groups)
                self.assign_groups(user, role_names) # Your existing assign_groups function
                user.save() # Save all changes (username, email, names, roles)

    def assign_groups(self, user, role_names):
        # (Your existing assign_groups function from previous examples)
        # Ensure it clears existing groups if that's the desired behavior,
        # or just adds new ones.
        # Example:
        # user.groups.clear() # If you want these to be the *only* roles
        current_group_names = set(user.groups.values_list('name', flat=True))
        target_group_names = set(role_names)

        groups_to_add = target_group_names - current_group_names
        groups_to_remove = current_group_names - target_group_names # Only if you want to enforce exact match

        for role_name in groups_to_add:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
                self.stdout.write(f"Added user {user.username} to group {role_name}")
            except Group.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Group '{role_name}' does not exist."))
        
        # Optional: remove groups user shouldn't be in anymore
        # for role_name in groups_to_remove:
        #     try:
        #         group = Group.objects.get(name=role_name)
        #         user.groups.remove(group)
        #         self.stdout.write(f"Removed user {user.username} from group {role_name}")
        #     except Group.DoesNotExist: # Should not happen if it was in current_group_names
        #         pass