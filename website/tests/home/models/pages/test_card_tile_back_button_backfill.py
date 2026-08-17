"""
Tests for the 0132 data migration that backfills the back button fields
(show_back_button / back_button_text) onto pre-existing "card_tiles" blocks
that were saved before those fields existed.

The back button belongs to the CardTilesBlock container - one button for
the whole set of tiles (A, B, C, ...), shown only when a tile is selected.
It only has a visible effect when at least one tile links to an
"anchor_page", so only card_tiles blocks with at least one such tile should
be backfilled.

The backfill only updates the live page row via page.save() - it does not
publish a revision, so the admin editor's draft/preview state is left as-is
and may not reflect the backfilled values until the page is next edited.
"""

import importlib

from django.apps import apps
from django.test import TestCase, override_settings
from wagtail.models import Locale, Page, Site

from home.models.pages.enhanced_standard import EnhancedStandardPage

backfill_module = importlib.import_module(
    "home.migrations.0132_alter_enhancedstandardpage_body"
)


@override_settings(
    GITHUB_SHA="test1234567",
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class BackfillCardTileBackButtonTest(TestCase):
    def setUp(self):
        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home-back-button-backfill-test")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        def _tile(header, link_type, link_value):
            return {
                "icon": 1,
                "icon_direction": "top",
                "card_header": header,
                "link": [{"type": link_type, "value": link_value}],
                "card_hover": True,
            }

        anchor_link_value = {
            "breadcrumb_title": "Anchor Tile",
            "body": [{"type": "paragraph", "value": "<p>Anchor body</p>"}],
        }

        # Simulates "old" data saved before show_back_button/back_button_text
        # existed on CardTilesBlock - those keys are simply absent.
        self.page_with_anchor_tile = EnhancedStandardPage(
            title="Card Tiles Backfill Test Page (anchor)",
            slug="card-tiles-backfill-test-page-anchor",
            body=[
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [
                            _tile("Anchor Tile", "anchor_page", anchor_link_value),
                            _tile(
                                "External Tile",
                                "external_url",
                                "https://example.com",
                            ),
                        ],
                        "default_content": [],
                    },
                }
            ],
        )
        home_page.add_child(instance=self.page_with_anchor_tile)

        self.page_without_anchor_tile = EnhancedStandardPage(
            title="Card Tiles Backfill Test Page (no anchor)",
            slug="card-tiles-backfill-test-page-no-anchor",
            body=[
                {
                    "type": "card_tiles",
                    "value": {
                        "tiles": [
                            _tile(
                                "External Tile",
                                "external_url",
                                "https://example.com",
                            ),
                        ],
                        "default_content": [],
                    },
                }
            ],
        )
        home_page.add_child(instance=self.page_without_anchor_tile)

    def test_backfill_enables_back_button_when_an_anchor_page_tile_exists(self):
        self.page_with_anchor_tile.refresh_from_db()
        self.assertIsNone(self.page_with_anchor_tile.latest_revision)

        backfill_module.backfill_back_button(apps=apps, schema_editor=None)

        self.page_with_anchor_tile.refresh_from_db()
        card_tiles_value = self.page_with_anchor_tile.body[0].value
        self.assertTrue(card_tiles_value["show_back_button"])
        self.assertEqual(card_tiles_value["back_button_text"], "Back")

        # The backfill only calls page.save(), not save_revision().publish(),
        # so no revision is created - the live row is updated directly.
        self.assertIsNone(self.page_with_anchor_tile.latest_revision)

    def test_backfill_skips_card_tiles_without_an_anchor_page_tile(self):
        backfill_module.backfill_back_button(apps=apps, schema_editor=None)

        self.page_without_anchor_tile.refresh_from_db()
        self.assertIsNone(self.page_without_anchor_tile.latest_revision)
        card_tiles_value = self.page_without_anchor_tile.body[0].value
        self.assertFalse(card_tiles_value["show_back_button"])
        self.assertFalse(card_tiles_value["back_button_text"])

    def test_backfill_is_idempotent(self):
        backfill_module.backfill_back_button(apps=apps, schema_editor=None)
        self.page_with_anchor_tile.refresh_from_db()
        card_tiles_value = self.page_with_anchor_tile.body[0].value
        first_show_back_button = card_tiles_value["show_back_button"]
        first_back_button_text = card_tiles_value["back_button_text"]

        backfill_module.backfill_back_button(apps=apps, schema_editor=None)
        self.page_with_anchor_tile.refresh_from_db()

        # No changes left to make, so the values should be unchanged.
        card_tiles_value = self.page_with_anchor_tile.body[0].value
        self.assertEqual(card_tiles_value["show_back_button"], first_show_back_button)
        self.assertEqual(card_tiles_value["back_button_text"], first_back_button_text)

    def test_backfill_uses_per_slug_override_text_for_practitioners_page(self):
        # Simulates an already-existing production "practitioners" page that
        # predates the back button fields - the initializer's create-if-not-
        # exists check means its "Back to Guidance" text never gets applied
        # by re-running the initializer, so the backfill must supply it.
        self.page_with_anchor_tile.slug = "practitioners"
        self.page_with_anchor_tile.save()

        backfill_module.backfill_back_button(apps=apps, schema_editor=None)

        self.page_with_anchor_tile.refresh_from_db()
        card_tiles_value = self.page_with_anchor_tile.body[0].value
        self.assertTrue(card_tiles_value["show_back_button"])
        self.assertEqual(card_tiles_value["back_button_text"], "Back to Guidance")
