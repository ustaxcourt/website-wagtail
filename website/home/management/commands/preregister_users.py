from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.conf import settings

# Define your users and their intended roles
# This could come from a CSV, a list, or another data source
USERS_TO_PREREGISTER = [
    {'email': 'Miriam.Miest-Moore.ctr@ustaxcourt.gov', 'first_name': 'Miriam', 'last_name': 'Miest-Moore', 'role_names': ['Editors']},
]

class Command(BaseCommand):
    help = 'Pre-registers users and assigns them to Wagtail/Django groups.'

    def handle(self, *args, **options):
        for user_data in USERS_TO_PREREGISTER:
            email = user_data['email']
            username = user_data.get('username', email) # Or derive username as per your SSO config

            # Check if user already exists by email or username to avoid duplicates
            if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User {email} or {username} already exists. Skipping."))
                # Optionally, update their groups if they exist
                user = User.objects.get(email=email) # or username
                self.assign_groups(user, user_data['role_names'])
                continue

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', '')
                )
                user.set_unusable_password() # They will log in via SSO
                user.is_staff = True # Assume all pre-registered users need admin access
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully created user: {email}"))

                self.assign_groups(user, user_data['role_names'])

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating user {email}: {e}"))

    def assign_groups(self, user, role_names):
        user.groups.clear() # Optional: Clear existing groups if you want to enforce only these roles
        for role_name in role_names:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
                self.stdout.write(f"Added user {user.email} to group {role_name}")
            except Group.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Group '{role_name}' does not exist. Please create it first in Django Admin or Wagtail Admin Settings."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error assigning group {role_name} to {user.email}: {e}"))
        user.save()