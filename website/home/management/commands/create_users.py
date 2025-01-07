from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from dataclasses import dataclass
import os


@dataclass
class UserConfig:
    username: str
    group_name: str
    email: str
    first_name: str
    last_name: str


# Define user_map with dataclass instances
user_map = {
    "Moderators": [
        UserConfig(
            username="moderator",
            group_name="Moderators",
            email="moderator@example.com",
            first_name="Moderator",
            last_name="User",
        )
    ],
    "Editors": [
        UserConfig(
            username="editor",
            group_name="Editors",
            email="editor@example.com",
            first_name="Editor",
            last_name="User",
        )
    ],
}

SUPERUSER_PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")


class Command(BaseCommand):
    help = "Update moderator password to default"

    def add_arguments(self, parser):
        parser.add_argument(
            "--group_name",
            type=str,
            help="Specify the group name (e.g., 'admin', 'moderator', 'editor')",
        )
        parser.add_argument(
            "--user_name",
            type=str,
            help="Specify the group name (e.g., 'admin', 'moderator', 'editor')",
        )

    def handle(self, *args, **kwargs):
        group_name = kwargs["group_name"]
        user_name = kwargs["user_name"]

        users = user_map[group_name]
        if user_name:
            users = [user for user in users if user.username == user_name]

        for user in users:
            if User.objects.filter(username=user.username).exists():
                u = User.objects.get(username=user.username)
                u.set_password(SUPERUSER_PASSWORD)
                u.save()
                print(
                    f"{user.first_name} password successfully changed and added to '{group_name}' group.'"
                )
            else:
                group, _ = Group.objects.get_or_create(name=group_name)
                u = User.objects.create_user(
                    username=user.username,
                    email=user.email,
                    password=SUPERUSER_PASSWORD,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )
                u.groups.add(group)
                print(
                    f"{user.first_name} account successfully created and added to '{group_name}' group.'"
                )
