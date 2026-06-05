"""
0122: Fix the JCDP page title in the DB.

The JCDP page was created via JudicialConductAndDisabilityProceduresPageInitializer
with title "Judicial Conduct and Disability Procedures" (no "Complaint"). The
initializer's title string was later corrected to "Judicial Conduct and Disability
Complaint Procedures" but its create() is a no-op once the page exists, and the
rules_and_guidance initializers are not wired into update_pages, so the existing
deployed page never gets re-titled. This migration updates title + seo_title on
the existing page and publishes a fresh revision.
"""

from django.db import migrations


CORRECT_TITLE = "Judicial Conduct and Disability Complaint Procedures"


def fix_jcdp_title(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="jcdp")
        except Page.DoesNotExist:
            logger.info("0122: jcdp page not found — skipping.")
            return

        specific = page.specific
        if specific.title == CORRECT_TITLE and specific.seo_title == CORRECT_TITLE:
            logger.info("0122: jcdp page title already correct — skipping.")
            return

        specific.title = CORRECT_TITLE
        specific.seo_title = CORRECT_TITLE
        specific.save()
        specific.save_revision().publish()
        logger.info(f"0122: jcdp page title set to {CORRECT_TITLE!r}.")
    except Exception as e:
        logger.warning(f"0122: could not update jcdp page title: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0124_seed_seminar_intro_text"),
    ]

    operations = [
        migrations.RunPython(fix_jcdp_title, noop),
    ]
