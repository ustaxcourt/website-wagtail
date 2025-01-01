from django.db import migrations


def create_homepage_meta(apps, schema_editor):
    HomePage = apps.get_model("home", "HomePage")

    homepage = HomePage.objects.first()

    if homepage:
        homepage.seo_title = "United States Tax Court"
        homepage.search_description = "Official Site of the United States Tax Court"
        homepage.save()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_home_page_entries"),
    ]

    operations = [
        migrations.RunPython(create_homepage_meta),
    ]
