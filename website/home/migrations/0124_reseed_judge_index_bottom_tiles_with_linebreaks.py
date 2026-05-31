"""
0124: Re-seed JudgeIndex.bottom_tiles so tile titles carry an explicit "\\n"
at the Figma-intended wrap point. Pairs with the shared QAT template's
`linebreaksbr` filter — see Option A in
docs/research/wag-1246-figma-mobile-width-vs-real-devices.md.
"""

from django.db import migrations


def reseed_with_linebreaks(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info("0124: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0124: JudgeIndex not found — skipping.")
            return

        # Clear so the guard in _seed_bottom_tiles allows a fresh seed.
        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        JudgesPageInitializer()._seed_bottom_tiles(page)
        logger.info("0124: bottom_tiles re-seeded with linebreak titles.")
    except Exception as e:
        logger.warning(f"0124: could not re-seed bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0123_force_reset_judge_index_bottom_tiles"),
    ]

    operations = [
        migrations.RunPython(reseed_with_linebreaks, noop),
    ]
