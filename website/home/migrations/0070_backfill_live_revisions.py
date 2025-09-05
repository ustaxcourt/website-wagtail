from django.db import migrations
from django.core.management import call_command


def run_backfill_live_revisions(apps, schema_editor):
    "Run custom backfill_live_revisions management command"

    try:
        call_command("backfill_live_revisions")
    except Exception as e:
        print(f"Warning: backfill_live_revisions failed: {e}")


def reverse_backfill_live_revisions(apps, schema_editor):
    # Reverse migration does nothing - we aren't making any schema changes and it is
    # a bit hard to un-backfill the data in this scenario because it'd be difficult
    # to figure out which records were added to original backfill operation
    pass


class Migration(migrations.Migration):
    dependencies = [("home", "0069_homepage_static_text_cards")]
    operations = [
        migrations.RunPython(
            run_backfill_live_revisions,
            reverse_backfill_live_revisions,
        ),
    ]
