from django.db import migrations

FA_ICON_TO_MD_ICON = {
    "": "",
    "fa-solid fa-1": "1",
    "fa-solid fa-2": "2",
    "fa-solid fa-3": "3",
    "fa-solid fa-check": "check",
    "fa-solid fa-exclamation": "exclamation",
    "fa-solid fa-book": "book_3",
    "fa-solid fa-building-columns": "account_balance",
    "fa-solid fa-calendar": "calendar_today",
    "fa-solid fa-chevron-right": "chevron_right",
    "fa-solid fa-file-pdf": "description",
    "fa-solid fa-file": "draft",
    "fa-solid fa-gavel": "gavel",
    "fa-solid fa-circle-info": "info",
    "fa-solid fa-link": "link_2",
    "fa-solid fa-scale-balanced": "balance",
    "fa-solid fa-user": "person",
    "fa-solid fa-video": "videocam",
    "fa-solid fa-gear": "settings",
    "fa-solid fa-briefcase": "work",
    "fa-solid fa-magnifying-glass": "search",
}


def migrate_icons_in_enhancedstandardpage_body(apps, schema_editor):
    connection = schema_editor.connection

    is_postgres = connection.vendor == "postgresql"

    body_column = "body::text" if is_postgres else "body"
    body_cast = "::jsonb" if is_postgres else ""

    with connection.cursor() as cursor:
        for icon in FA_ICON_TO_MD_ICON:
            cursor.execute(
                f"UPDATE home_enhancedstandardpage SET body = replace({body_column}, %s, %s){body_cast} WHERE {body_column} LIKE %s",
                [icon, FA_ICON_TO_MD_ICON[icon], f"%{icon}%"],
            )


def migrate_icons_in_navigation_ribbons(apps, schema_editor):
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        for icon in FA_ICON_TO_MD_ICON:
            cursor.execute(
                "UPDATE home_navigationribbonlink SET icon = %s WHERE icon = %s",
                [FA_ICON_TO_MD_ICON[icon], icon],
            )


def migrate_icons_in_revisions(apps, schema_editor):
    connection = schema_editor.connection

    is_postgres = connection.vendor == "postgresql"

    content_column = "content::text" if is_postgres else "content"
    content_cast = "::jsonb" if is_postgres else ""

    with connection.cursor() as cursor:
        for icon in FA_ICON_TO_MD_ICON:
            cursor.execute(
                f"UPDATE wagtailcore_revision SET content = replace({content_column}, %s, %s){content_cast} WHERE {content_column} LIKE %s",
                [icon, FA_ICON_TO_MD_ICON[icon], f"%{icon}%"],
            )


def migrate_icons(apps, schema_editor):
    migrate_icons_in_enhancedstandardpage_body(apps, schema_editor)
    migrate_icons_in_navigation_ribbons(apps, schema_editor)
    migrate_icons_in_revisions(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0147_alter_directoryindex_body_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_icons, migrations.RunPython.noop),
    ]
