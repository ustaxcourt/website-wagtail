from django.db import migrations


def set_all_newsitems_to_news(apps, schema_editor):
    """Set all existing NewsItem category values to 'news' before removing the field."""
    NewsItem = apps.get_model("home", "NewsItem")
    NewsItem.objects.exclude(category="news").update(category="news")


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0097_alter_enhancedstandardpage_body"),
    ]

    operations = [
        migrations.RunPython(
            set_all_newsitems_to_news,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="newsitem",
            name="category",
        ),
    ]
