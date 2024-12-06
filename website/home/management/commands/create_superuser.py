from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import os

username = "admin"
email = "admin@example.com"
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")

class Command(BaseCommand):
    help = 'Description of your script'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=SUPERUSER_PASSWORD)
            print(f"Superuser '{username}' created.")
        else:
            print(f"Superuser '{username}' already exists.")
