import os
from django.contrib.auth.models import User

SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")

u = User.objects.get(username="admin")
u.set_password(SUPERUSER_PASSWORD)
u.save()