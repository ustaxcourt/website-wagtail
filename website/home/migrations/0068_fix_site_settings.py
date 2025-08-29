import os
from django.db import migrations


def update_site_forward(apps, schema_editor):
    """
    Update the default Wagtail Site object with the correct hostname,
    port, and site name from environment variables.
    """
    Site = apps.get_model("wagtailcore", "Site")

    # Get values from environment variables, with sensible defaults
    hostname = os.getenv("DOMAIN_NAME")
    port = os.getenv("WAGTAIL_PORT", 80)
    site_name = os.getenv("WAGTAIL_SITE_NAME", "Lower environment site")

    # Use update_or_create to safely update the default site,
    # or create it if it doesn't exist.
    Site.objects.update_or_create(
        is_default_site=True,
        defaults={
            "hostname": hostname,
            "port": port,
            "site_name": site_name,
            "root_url": hostname,
        },
    )


def update_site_backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0067_alter_enhancedstandardpage_body"),
    ]

    operations = [
        migrations.RunPython(update_site_forward, update_site_backward),
    ]
