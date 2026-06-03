"""
0131: Delete stray JudgeRole rows whose role_name is the pluralized form of a
JudgeProfile title.

`JudgeRole.role_name` is a freeform CharField; the only intentional roles
created by the seeder are "Chief Judge" and "Chief Special Trial Judge".
Sandbox had a JudgeRole with role_name "Senior Special Trial Judges" (plural)
linked to Judge Carluzzo, which caused the public Judges page to render his
role label as the plural form. The page falls back to JudgeProfile.title
(which is always singular) when no JudgeRole exists for a judge, so removing
the stray rows is enough to restore the singular label.
"""

from django.db import migrations


PLURAL_TYPE_NAMES = [
    "Judges",
    "Senior Judges",
    "Special Trial Judges",
    "Senior Special Trial Judges",
]


def delete_stray_pluralized_roles(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    JudgeRole = apps.get_model("home", "JudgeRole")

    qs = JudgeRole.objects.filter(role_name__in=PLURAL_TYPE_NAMES)
    count = qs.count()
    if not count:
        logger.info("0131: no stray pluralized JudgeRole rows — skipping.")
        return

    for row in qs:
        logger.info(
            f"0131: deleting JudgeRole id={row.pk} role_name={row.role_name!r} "
            f"judge_id={row.judge_id}"
        )
    qs.delete()
    logger.info(f"0131: deleted {count} stray pluralized JudgeRole row(s).")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0130_revert_jcdp_page_title"),
    ]

    operations = [
        migrations.RunPython(delete_stray_pluralized_roles, noop),
    ]
