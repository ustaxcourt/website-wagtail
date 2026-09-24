from django.db import migrations


def assign_report_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    news_ct, _ = ContentType.objects.get_or_create(app_label="home", model="newsitem")
    news_perm, _ = Permission.objects.get_or_create(
        codename="view_newsitem",
        content_type=news_ct,
        defaults={"name": "Can view news item"},
    )

    def_ct, _ = ContentType.objects.get_or_create(
        app_label="search", model="definitionsquery"
    )
    def_perm, _ = Permission.objects.get_or_create(
        codename="view_definitionsquery",
        content_type=def_ct,
        defaults={"name": "Can view Definition Search Query"},
    )

    for group_name in ["Editors", "Moderators", "Administrators"]:
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.add(news_perm, def_perm)


def remove_report_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        def_perm = Permission.objects.get(
            codename="view_definitionsquery",
            content_type__app_label="search",
        )
        for group_name in ["Editors", "Moderators", "Administrators"]:
            try:
                group = Group.objects.get(name=group_name)
                group.permissions.remove(def_perm)
            except Group.DoesNotExist:
                pass
    except Permission.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0139_alter_enhancedstandardpage_body"),
    ]

    operations = [
        migrations.RunPython(
            assign_report_permissions,
            remove_report_permissions,
        ),
    ]
