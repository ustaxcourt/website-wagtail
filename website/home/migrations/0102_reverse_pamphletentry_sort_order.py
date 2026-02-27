from django.db import migrations


def reverse_pamphlet_sort_order(apps, schema_editor):
    PamphletEntry = apps.get_model("home", "PamphletEntry")

    entries = list(
        PamphletEntry.objects.filter(sort_order__isnull=False).order_by(
            "sort_order", "id"
        )
    )

    if not entries:
        return

    sort_orders = [e.sort_order for e in entries]
    reversed_orders = list(reversed(sort_orders))

    for entry, new_sort_order in zip(entries, reversed_orders):
        entry.sort_order = new_sort_order

    PamphletEntry.objects.bulk_update(entries, ["sort_order"])


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0101_alter_pamphletentry_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            reverse_pamphlet_sort_order,
            migrations.RunPython.noop,
        ),
    ]
