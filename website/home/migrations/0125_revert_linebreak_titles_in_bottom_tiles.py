"""
0125: Revert Option A — re-seed JudgeIndex.bottom_tiles back to plain titles
(no embedded newlines). Option A was tried in 0124 + the |linebreaksbr filter
in quick_access_tile_block.html; rolling back per UX preference. See
docs/research/wag-1246-figma-mobile-width-vs-real-devices.md.
"""

from django.db import migrations


def revert_to_plain_titles(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info("0125: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0125: JudgeIndex not found — skipping.")
            return

        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        JudgesPageInitializer()._seed_bottom_tiles(page)
        logger.info("0125: bottom_tiles reverted to plain titles.")
    except Exception as e:
        logger.warning(f"0125: could not revert bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0124_reseed_judge_index_bottom_tiles_with_linebreaks"),
    ]

    operations = [
        migrations.RunPython(revert_to_plain_titles, noop),
    ]
