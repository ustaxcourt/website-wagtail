from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from home.utils.secrets import get_secret

username = "admin"
email = "admin@example.com"
SUPERUSER_PASSWORD = get_secret("WAGTAIL_ADMIN_PASSWORD")


class Command(BaseCommand):
    help = "Update superuser admin password to default stored in secrets"

    def handle(self, *args, **kwargs):
        if User.objects.filter(username=username).exists():
            u = User.objects.get(username="admin")
            u.set_password(SUPERUSER_PASSWORD)
            u.save()
            print("Superuser password successfully changed")
        else:
            print("Superuser account does not exist yet")
