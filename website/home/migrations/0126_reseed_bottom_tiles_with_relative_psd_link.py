"""
0126: Re-seed JudgeIndex.bottom_tiles so the PSD tile uses a relative URL.

Pre-QAT-reuse, the PSD tile link was rendered in-template as
`{{ page.url }}private-seminar-disclosures/` — a relative URL that worked on
every environment. The QAT seeder regressed this by storing
`{judges_page.full_url}private-seminar-disclosures/`, which bakes in the
hostname (and on local dev, the missing port) at migration time and breaks
navigation. This migration clears `bottom_tiles` and re-seeds with the
corrected relative-URL seeder.
"""

from django.db import migrations


def reseed_with_relative_psd_link(apps, schema_editor):
    import logging

    logger = logging.getLogger(__name__)
    try:
        from wagtail.models import Page

        try:
            page = Page.objects.get(slug="judges")
        except Page.DoesNotExist:
            logger.info("0126: judges page not found — skipping.")
            return

        from home.models.pages.judge_index import JudgeIndex

        try:
            judge_index = JudgeIndex.objects.get(pk=page.pk)
        except JudgeIndex.DoesNotExist:
            logger.info("0126: JudgeIndex not found — skipping.")
            return

        judge_index.bottom_tiles = []
        judge_index.save()

        from home.management.commands.pages.about_the_court.judges_page import (
            JudgesPageInitializer,
        )

        JudgesPageInitializer()._seed_bottom_tiles(page)
        logger.info("0126: bottom_tiles re-seeded with relative PSD link.")
    except Exception as e:
        logger.warning(f"0126: could not re-seed bottom_tiles: {e}")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0125_revert_linebreak_titles_in_bottom_tiles"),
    ]

    operations = [
        migrations.RunPython(reseed_with_relative_psd_link, noop),
    ]
