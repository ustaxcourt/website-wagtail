from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import os

username = "admin"
email = "admin@example.com"
DJANGO_SUPERUSER_PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")


class Command(BaseCommand):
    help = "Update superuser admin password to default stored in secrets"

    def handle(self, *args, **kwargs):
        if User.objects.filter(username=username).exists():
            u = User.objects.get(username="admin")
            u.set_password(DJANGO_SUPERUSER_PASSWORD)
            u.save()
            print("Superuser password successfully changed")
        else:
            print("Superuser account does not exist yet")
