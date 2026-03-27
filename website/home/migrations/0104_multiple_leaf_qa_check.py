from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0103_alter_pamphletentry_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop,
            migrations.RunPython.noop,
        ),
    ]
