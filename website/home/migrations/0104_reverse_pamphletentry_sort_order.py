from django.db import migrations


def reverse_pamphlet_sort_order(apps, schema_editor):
    PamphletEntry = apps.get_model("home", "PamphletEntry")

    # sort_order is NULL for all entries (added in previous migration),
    # so order by -id: most recent id gets the lowest sort_order (0)
    entries = list(PamphletEntry.objects.order_by("-id"))

    if not entries:
        return

    for i, entry in enumerate(entries):
        entry.sort_order = i

    PamphletEntry.objects.bulk_update(entries, ["sort_order"])


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0103_alter_pamphletentry_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            reverse_pamphlet_sort_order,
            migrations.RunPython.noop,
        ),
    ]
