"""
Data migration: seed the two bottom QuickAccessTiles on the JudgeIndex page.

This runs after 0119_add_judge_index_bottom_tiles (which added the empty field).
Without this, existing environments that were seeded before the StreamField existed
would have no tile data, causing the tiles section to be silently hidden in the template.
"""

from django.db import migrations


def seed_bottom_tiles(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info(
                "0120: judges page not found — bottom_tiles seed skipped (fresh install will create it via create_pages)."
            )
            return

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        initializer = JudgesPageInitializer()
        initializer._seed_bottom_tiles(page)
        logger.info("0120: bottom_tiles seed completed.")
    except Exception as e:
        # Non-fatal: log and continue so the migration doesn't block a deploy
        logger.warning(f"0120: could not seed bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0119_add_judge_index_bottom_tiles"),
    ]

    operations = [
        migrations.RunPython(seed_bottom_tiles, noop),
    ]
