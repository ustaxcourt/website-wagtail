from django.db import migrations
from django.core.management import call_command


def run_backfill_live_revisions(apps, schema_editor):
    "Run custom backfill_live_revisions management command"

    try:
        call_command("backfill_live_revisions")
    except Exception as e:
        print(f"Warning: backfill_live_revisions failed: {e}")


def reverse_backfill_live_revisions(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("home", "0067_alter_enhancedstandardpage_body")]
    operations = [
        migrations.RunPython(
            run_backfill_live_revisions,
            reverse_backfill_live_revisions,
        ),
    ]
