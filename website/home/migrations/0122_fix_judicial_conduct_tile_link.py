"""
0122: Fix the Judicial Conduct tile link.

Migration 0121 re-seeded bottom_tiles but the JCDP page lookup used the wrong
slug, so the JCDP tile rendered without a link. This migration locates the
JCDP page and patches the second tile's link in place.
"""

from django.db import migrations


def fix_judicial_conduct_link(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            judge_index_page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info("0122: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=judge_index_page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0122: JudgeIndex not found — skipping.")
            return

        # Clear bottom_tiles and re-seed with the fixed JCDP slug lookup.
        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        initializer = JudgesPageInitializer()
        initializer._seed_bottom_tiles(judge_index_page)
        logger.info("0122: bottom_tiles re-seeded with fixed JCDP link.")
    except Exception as e:
        logger.warning(f"0122: could not patch JCDP tile link: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0121_reseed_judge_index_bottom_tiles"),
    ]

    operations = [
        migrations.RunPython(fix_judicial_conduct_link, noop),
    ]
