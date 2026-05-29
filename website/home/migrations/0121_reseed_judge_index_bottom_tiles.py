"""
0121: Re-seed JudgeIndex.bottom_tiles with the correct ListBlock data format.

Migration 0120 seeded tiles using StreamBlock-style {"type": "item", "value": {...}}
wrappers. However, QuickAccessTilesBlock.tiles is a ListBlock, which expects a plain
list of raw dicts with no type/value wrapper. This migration clears the bad data and
re-seeds using the corrected _build_bottom_tiles_data() in JudgesPageInitializer.
"""

from django.db import migrations


def reseed_bottom_tiles(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info("0121: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0121: JudgeIndex not found — skipping.")
            return

        # Clear any previously seeded (wrong-format) tiles so the guard in
        # _seed_bottom_tiles allows re-seeding.
        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        initializer = JudgesPageInitializer()
        initializer._seed_bottom_tiles(page)
        logger.info("0121: bottom_tiles re-seeded with correct ListBlock format.")
    except Exception as e:
        logger.warning(f"0121: could not re-seed bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0120_seed_judge_index_bottom_tiles"),
    ]

    operations = [
        migrations.RunPython(reseed_bottom_tiles, noop),
    ]
