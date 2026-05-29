"""
0123: Force-reset JudgeIndex.bottom_tiles to AC-correct values.

The sandbox tiles were edited via the Wagtail admin into a state that no longer
matches AC (titles split between title+description and one link pointing to an
external test URL). Clear and re-seed using JudgesPageInitializer so the page
renders the two tiles as specified:
  1. "Private Seminar Disclosures" -> /judges/private-seminar-disclosures/
  2. "Judicial Conduct and Disability Complaint Procedures" -> jcdp page
"""

from django.db import migrations


def force_reset_bottom_tiles(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info("0123: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0123: JudgeIndex not found — skipping.")
            return

        # Clear any manual admin edits so the guard in _seed_bottom_tiles allows
        # a fresh seed.
        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        JudgesPageInitializer()._seed_bottom_tiles(page)
        logger.info("0123: bottom_tiles force-reset to AC values.")
    except Exception as e:
        logger.warning(f"0123: could not force-reset bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0122_fix_judicial_conduct_tile_link"),
    ]

    operations = [
        migrations.RunPython(force_reset_bottom_tiles, noop),
    ]
