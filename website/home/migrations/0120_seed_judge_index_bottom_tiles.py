"""
0120: Seed JudgeIndex.bottom_tiles with the final AC-correct tile data.

Consolidates a long chain of incremental fixes (originally migrations
0120-0128, 0130, 0131) that were never deployed beyond a personal sandbox.
The end state seeded here is exactly what those incremental migrations
arrived at and matches the page initializer's `_build_bottom_tiles_data`:

  * Tile 1 — "Private Seminar Disclosures" linking to
    /judges/private-seminar-disclosures/ (relative URL — portable across envs)
  * Tile 2 — "Judicial Conduct and Disability Complaint Procedures" linking
    to the JCDP page via related_page (resolved at render time)

Both tiles share `tiles_hover_enabled=True` and `icon_position
="desktop_top_mobile_left"`. The migration is idempotent: it only seeds when
`bottom_tiles` is empty, so reapplying or running update_pages later won't
clobber admin edits.
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
            logger.info("0120: judges page not found — skipping bottom_tiles seed.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0120: JudgeIndex not found — skipping bottom_tiles seed.")
            return

        if judge_index.bottom_tiles:
            logger.info("0120: bottom_tiles already set — skipping seed.")
            return

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        # Delegates to the page initializer's data-builder so the migration
        # and the seed command share a single source of truth for tile content.
        JudgesPageInitializer()._seed_bottom_tiles(page)
        logger.info("0120: bottom_tiles seeded.")
    except Exception as e:
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
