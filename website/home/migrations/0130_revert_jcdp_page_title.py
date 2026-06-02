"""
0130: Revert the JCDP page title back to the official name.

A WAG-1247 migration (`0122_fix_jcdp_page_title`) previously set the title to
"Judicial Conduct and Disability Complaint Procedures". Per the PO, "Complaint"
was a placeholder used only because there cannot be two pages with the same
name, and the official title is "Judicial Conduct and Disability Procedures".
This migration restores the official title on any environment whose DB still
reflects the placeholder value.
"""

from django.db import migrations


OFFICIAL_TITLE = "Judicial Conduct and Disability Procedures"


def revert_jcdp_title(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="jcdp")
        except Page.DoesNotExist:
            logger.info("0130: jcdp page not found — skipping.")
            return

        specific = page.specific
        if specific.title == OFFICIAL_TITLE and specific.seo_title == OFFICIAL_TITLE:
            logger.info("0130: jcdp page title already official — skipping.")
            return

        specific.title = OFFICIAL_TITLE
        specific.seo_title = OFFICIAL_TITLE
        specific.save()
        specific.save_revision().publish()
        logger.info(f"0130: jcdp page title reverted to {OFFICIAL_TITLE!r}.")
    except Exception as e:
        logger.warning(f"0130: could not revert jcdp page title: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0129_dedupe_and_unique_judge_collection_orderable"),
    ]

    operations = [
        migrations.RunPython(revert_jcdp_title, noop),
    ]
