"""
0127: Re-seed JudgeIndex.bottom_tiles to AC-correct values after another round
of admin edits broke the sandbox state (split titles, PSD link replaced with an
external test URL). Clear and re-seed via JudgesPageInitializer.
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
            logger.info("0127: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0127: JudgeIndex not found — skipping.")
            return

        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        JudgesPageInitializer()._seed_bottom_tiles(page)
        logger.info("0127: bottom_tiles re-seeded.")
    except Exception as e:
        logger.warning(f"0127: could not re-seed bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0126_reseed_bottom_tiles_with_relative_psd_link"),
    ]

    operations = [
        migrations.RunPython(reseed_bottom_tiles, noop),
    ]
