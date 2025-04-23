from .base import *  # noqa: F403
import json
import urllib.request
import os
from .base import ALLOWED_HOSTS


def _task_ips():
    """Return the task’s IPv4 address(es) from the ECS metadata API."""
    meta = os.getenv("ECS_CONTAINER_METADATA_URI_V4") or os.getenv(
        "ECS_CONTAINER_METADATA_URI"
    )
    if not meta:
        return []

    try:
        with urllib.request.urlopen(f"{meta}/task", timeout=0.2) as r:
            data = json.load(r)
            # First container in the task is usually “ours”
            nets = data["Containers"][0]["Networks"]
            return [ip for net in nets for ip in net["IPv4Addresses"]]
    except Exception:
        return []


os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "ustcAdminPW!")

try:
    from .local import *  # noqa: F403

except ImportError:
    pass

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True
BASE_URL = f'https://{os.getenv("DOMAIN_NAME")}'
ENVIRONMENT = "sandbox"

ALLOWED_HOSTS += _task_ips()
