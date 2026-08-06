"""
0133: Backfill the new CardTilesBlock back button fields on existing
"card_tiles" blocks so the (single, shared) back button shows up by default
for card tile sets that were created before the field existed.

The back button belongs to the CardTilesBlock container (not to individual
tiles) - one button governs the whole set of tiles (A, B, C, ...) and is
shown whenever any tile is selected (e.g. p/a, p/b) and hidden on the
default view showing all tiles. It only has a visible effect when at least
one tile links to an "anchor_page" (the only link type that keeps the user
on the same page/URL param instead of navigating away), so only card_tiles
blocks with at least one such tile are backfilled.

Uses the live model (not the historical/frozen migration model) so we can
call save_revision().publish(). A plain page.save() would update the live
page row but leave the latest revision stale, so the admin editor would
still show the old (no back button) content even though the public page
had it. See SeedBottomTilesRevisionTest for the regression this mirrors.
"""

import logging

from django.db import migrations

logger = logging.getLogger(__name__)

DEFAULT_BACK_BUTTON_TEXT = "Back"

# Per-page overrides for the generic default text, keyed by page slug, so
# pages whose initializer specifies custom back button text (e.g. the
# Guidance for Practitioners page) get that same text when backfilled on an
# environment where the page already existed before this field was added
# (the initializer's create-if-not-exists check means it never re-applies
# this text to an existing page).
BACK_BUTTON_TEXT_BY_SLUG = {
    "practitioners": "Back to Guidance",
}


def backfill_back_button(apps, schema_editor):
    from home.models.pages.enhanced_standard import EnhancedStandardPage  # noqa: no-direct-model-imports-in-migrations — needs the live model to call save_revision().publish()

    for page in EnhancedStandardPage.objects.all():
        changed = False
        back_button_text = BACK_BUTTON_TEXT_BY_SLUG.get(
            page.slug, DEFAULT_BACK_BUTTON_TEXT
        )

        for block in page.body:
            if block.block_type != "card_tiles":
                continue

            has_anchor_page_tile = any(
                tile["link"] and tile["link"][0].block_type == "anchor_page"
                for tile in block.value["tiles"]
            )
            if not has_anchor_page_tile:
                continue

            if not block.value["show_back_button"]:
                block.value["show_back_button"] = True
                changed = True

            if not block.value["back_button_text"]:
                block.value["back_button_text"] = back_button_text
                changed = True

        if changed:
            try:
                page.save_revision().publish()
                logger.info(
                    f"0133: backfilled back button on EnhancedStandardPage id={page.pk}."
                )
            except Exception as e:
                logger.warning(
                    f"0133: could not backfill back button on "
                    f"EnhancedStandardPage id={page.pk}: {e}"
                )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0132_alter_enhancedstandardpage_body"),
    ]

    operations = [
        migrations.RunPython(backfill_back_button, noop),
    ]
